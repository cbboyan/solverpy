from typing import TYPE_CHECKING
import os
import logging
from collections import defaultdict

import numpy
import scipy
from sklearn.datasets import load_svmlight_file, dump_svmlight_file

from ..tools import human
from ..tools.extprocess import extprocess
from ..benchmark.reports import progress

if TYPE_CHECKING:
   from scipy.sparse import spmatrix
   from numpy import ndarray

logger = logging.getLogger(__name__)


def datafiles(f_in: str) -> tuple[str, str]:
   z_data = f_in + "-data.npz"
   z_label = f_in + "-label.npz"
   return (z_data, z_label)


def iscompressed(f_in: str) -> bool:
   return all(map(os.path.isfile, datafiles(f_in)))


def exists(f_in: str) -> bool:
   return iscompressed(f_in) or os.path.isfile(f_in)


def size(f_in: str) -> int:
   if iscompressed(f_in):
      return sum(os.path.getsize(f) for f in datafiles(f_in))
   else:
      return os.path.getsize(f_in)


def format(f_in: str) -> str:
   if iscompressed(f_in):
      return "binary/npz"
   if os.path.isfile(f_in):
      return "text/svm"
   return "unknown"


def load(f_in: str) -> tuple["spmatrix", "ndarray"]:
   logger.info(
      f"Loading trains of size {human.humanbytes(size(f_in))} from `{f_in}`.")
   if iscompressed(f_in):
      logger.debug(f"loading compressed data")
      (z_data, z_label) = datafiles(f_in)
      data = scipy.sparse.load_npz(z_data)
      label = numpy.load(z_label, allow_pickle=True)["label"]
      logger.debug(f"compressed data loaded")
   else:
      logger.debug(f"loading uncompressed data")
      (data, label) = load_svmlight_file(f_in, zero_based=True)  # type: ignore
      logger.debug(f"uncompressed data loaded")
   logger.info("Trains loaded.")
   return (data, label)


def save(data: "spmatrix", label: "ndarray", f_in: str) -> None:
   (z_data, z_label) = datafiles(f_in)
   logger.debug(f"saving compressed data to {z_data}")
   scipy.sparse.save_npz(z_data, data, compressed=True)
   logger.debug(f"saving compressed labels to {z_label}")
   numpy.savez_compressed(z_label, label=label)
   logger.info(f"Saved trains: {f_in}")


@extprocess
def compress(f_in: str, keep: bool = False) -> None:
   logger.info(
      f"Compressing trains of size {human.humanbytes(size(f_in))} from `{f_in}`."
   )
   if iscompressed(f_in):
      logger.warning(f"Trains {f_in} are already compressed.  Skipped.")
      return
   size_in = size(f_in)  # size before compression
   (data, label) = load_svmlight_file(f_in, zero_based=True)  # type: ignore
   save(data, label, f_in)
   report = progress.compress(f_in, size_in, size(f_in), data, label)
   if iscompressed(f_in) and not keep:
      logger.debug(f"deleting the uncompressed file")
      os.remove(f_in)
   logger.info(
      f"Trains compressed to {human.humanbytes(size(f_in))}.\n{report}")

@extprocess
def decompress(f_in: str, keep: bool = True) -> None:
   logger.info(
      f"Decompressing trains of size {human.humanbytes(size(f_in))} from `{f_in}`."
   )
   if not iscompressed(f_in):
      logger.warning(f"Trains `{f_in}` are not compressed.  Skipped.")
      return
   (data, label) = load(f_in)
   logger.debug(f"dumping trains to {f_in}")
   dump_svmlight_file(data, label, f_in)
   logger.debug(
      f"trains dumped; uncompressed size: {human.humanbytes(os.path.getsize(f_in))}"
   )
   if os.path.isfile(f_in) and not keep:
      logger.debug(f"deleting the compressed files")
      for f in datafiles(f_in):
         os.remove(f)
   logger.info(
      f"Trains decompressed to {human.humanbytes(os.path.getsize(f_in))}.")

@extprocess
def merge(
   f_in1: (str | None) = None,
   f_in2: (str | None) = None,
   data1: (tuple["spmatrix", "ndarray"] | None) = None,
   data2: (tuple["spmatrix", "ndarray"] | None) = None,
   f_out: (str | None) = None,
) -> tuple["spmatrix", "ndarray"] | None:
   assert data1 or f_in1
   assert data2 or f_in2
   if f_in1 and f_in2:
      logger.info(f"Merging trains: {f_in1} and {f_in2}")
   (d1, l1) = data1 if data1 else load(f_in1)  # type: ignore
   (d2, l2) = data2 if data2 else load(f_in2)  # type: ignore
   logger.info(
      f"Merging data of shapes: {d1.shape[0]}x{d1.shape[1]} and {d2.shape[0]}x{d2.shape[1]}"
   )
   d = scipy.sparse.vstack((d1, d2))
   logger.info(f"Merging labels of shapes: {l1.shape[0]} and {l2.shape[0]}")
   l = numpy.concatenate((l1, l2))
   if f_out:
      save(d, l, f_out)
      return None
   return (d, l)


def deconflict(xs: "spmatrix", ys: "ndarray") -> tuple["spmatrix", "ndarray"]:
   "Find conflicting positive and negative samples and remove the negative ones."
   assert xs.shape[0] == ys.shape[0]
   logger.info("Looking up conflicting samples.")
   logger.debug("building samples map")
   dups = defaultdict(list)
   for i in range(xs.shape[0]):
      row = xs.getrow(i)
      key = (tuple(row.indices), tuple(row.data))
      dups[key].append(i)
   logger.debug("marking conflicting negative samples")
   todel = set()
   for ids in dups.values():
      if len(ids) < 2:
         continue
      td = []
      onepos = False
      for i in ids:
         if ys[i] == 0:
            td.append(i)  # mark negative indicies to be removed
         else:
            onepos = True  # there is at least one positive
      if onepos:
         todel.update(td)
   logger.debug("deleting marked rows")
   keep = [i for i in range(xs.shape[0]) if i not in todel]
   xs0 = xs[keep]  # type: ignore
   ys0 = ys[keep]
   logger.info("\n".join([
      "Data shape difference:",
      f"\t{xs.shape} --> {xs0.shape}",
      f"\t{ys.shape} --> {ys0.shape}",
   ]))
   return (xs0, ys0)
