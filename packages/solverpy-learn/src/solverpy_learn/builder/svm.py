from typing import TYPE_CHECKING
import os
import glob
import io
import logging
import multiprocessing
from collections import defaultdict

import numpy
import scipy
from sklearn.datasets import load_svmlight_file, dump_svmlight_file

from solverpy.tools import human
from .plugins.trains import rellink

if TYPE_CHECKING:
   from scipy.sparse import spmatrix
   from numpy import ndarray

logger = logging.getLogger(__name__)


def chunkpath(f_in: str, n: int) -> tuple[str, str]:
   return (f"{f_in}-chunk{n:04d}-data.npz", f"{f_in}-chunk{n:04d}-label.npz")


def chunkfiles(f_in: str) -> list[tuple[str, str]]:
   paths = sorted(glob.glob(f"{f_in}-chunk*-data.npz"))
   suffix = "-data.npz"
   return [(p, p[:-len(suffix)] + "-label.npz") for p in paths]


def ischunked(f_in: str) -> bool:
   return len(chunkfiles(f_in)) > 0


def rawchunkpath(f_in: str, n: int) -> str:
   return f"{f_in}-raw{n:04d}"


def rawchunkfiles(f_in: str) -> list[str]:
   return sorted(glob.glob(f"{f_in}-raw[0-9][0-9][0-9][0-9]"))


def israwchunked(f_in: str) -> bool:
   return len(rawchunkfiles(f_in)) > 0


def exists(f_in: str) -> bool:
   return ischunked(f_in) or israwchunked(f_in) or os.path.isfile(f_in)


def size(f_in: str) -> int:
   if ischunked(f_in):
      return sum(
         os.path.getsize(p) + os.path.getsize(q)
         for (p, q) in chunkfiles(f_in)
      )
   if israwchunked(f_in):
      return sum(os.path.getsize(p) for p in rawchunkfiles(f_in))
   return os.path.getsize(f_in)


def format(f_in: str) -> str:
   if ischunked(f_in):
      return "binary/chunks"
   if israwchunked(f_in):
      return "text/raw-chunks"
   if os.path.isfile(f_in):
      return "text/svm"
   return "unknown"


def save_chunk(data: "spmatrix", label: "ndarray", f_in: str, n: int) -> None:
   (z_data, z_label) = chunkpath(f_in, n)
   d_out = os.path.dirname(z_data)
   if d_out:
      os.makedirs(d_out, exist_ok=True)
   scipy.sparse.save_npz(z_data, data, compressed=True)
   numpy.savez_compressed(z_label, label=label)
   logger.debug(f"saved chunk {n}: {z_data}")


def _compress_batch(lines: list[str], f_in: str, n: int) -> None:
   buf = io.BytesIO("".join(lines).encode())
   (data, label) = load_svmlight_file(buf, zero_based=True)  # type: ignore
   save_chunk(data, label, f_in, n)


def compress(f_in: str, keep: bool = False, chunk_size: int = 1_000_000) -> None:
   if ischunked(f_in):
      logger.warning(f"Trains {f_in} are already chunked.  Skipped.")
      return
   if not os.path.isfile(f_in):
      logger.warning(f"No trains to compress: {f_in}.")
      return
   logger.info(
      f"Compressing trains of size {human.humanbytes(size(f_in))} from `{f_in}`.")
   n = 0
   batch: list[str] = []
   with open(f_in) as fh:
      for line in fh:
         batch.append(line)
         if len(batch) >= chunk_size:
            _compress_batch(batch, f_in, n)
            n += 1
            batch = []
   if batch:
      _compress_batch(batch, f_in, n)
      n += 1
   if not keep:
      os.remove(f_in)
   logger.info(
      f"Trains compressed to {n} chunks, {human.humanbytes(size(f_in))} total.")


def _compress_raw(raw_path: str, f_in: str, n: int) -> None:
   with open(raw_path) as fh:
      lines = fh.readlines()
   buf = io.BytesIO("".join(lines).encode())
   (data, label) = load_svmlight_file(buf, zero_based=True)  # type: ignore
   save_chunk(data, label, f_in, n)
   os.remove(raw_path)


def rawcompress(f_in: str, cores: int | None = None) -> None:
   raws = rawchunkfiles(f_in)
   if not raws:
      logger.warning(f"No raw chunks found: {f_in}.")
      return
   logger.info(
      f"Compressing {len(raws)} raw chunks of size {human.humanbytes(size(f_in))} from `{f_in}`."
   )
   args = [(raw, f_in, n) for (n, raw) in enumerate(raws)]
   if len(args) == 1:
      _compress_raw(*args[0])
   else:
      with multiprocessing.get_context("fork").Pool(cores) as pool:
         pool.starmap(_compress_raw, args)
   logger.info(
      f"Compressed to {len(raws)} NPZ chunks, {human.humanbytes(size(f_in))} total.")


def _load_chunk(p: str, q: str) -> tuple["spmatrix", "ndarray"]:
   return (scipy.sparse.load_npz(p), numpy.load(q, allow_pickle=True)["label"])


def _load_rawchunk(raw_path: str) -> tuple["spmatrix", "ndarray"]:
   return load_svmlight_file(raw_path, zero_based=True)  # type: ignore


def _stack_pairs(
   pairs: list[tuple["spmatrix", "ndarray"]]
) -> tuple["spmatrix", "ndarray"]:
   datas = [d for (d, _) in pairs]
   labels = [lbl for (_, lbl) in pairs]
   max_cols = max(d.shape[1] for d in datas)
   normalized = [
      scipy.sparse.csr_matrix(
         (d.data, d.indices, d.indptr), shape=(d.shape[0], max_cols)
      ) if d.shape[1] < max_cols else d
      for d in datas
   ]
   return (scipy.sparse.vstack(normalized), numpy.concatenate(labels))


def load(f_in: str, cores: int | None = None) -> tuple["spmatrix", "ndarray"]:
   logger.info(
      f"Loading trains of size {human.humanbytes(size(f_in))} from `{f_in}`.")
   if ischunked(f_in):
      chunks = chunkfiles(f_in)
      if len(chunks) == 1:
         pairs = [_load_chunk(*chunks[0])]
      else:
         with multiprocessing.get_context("fork").Pool(cores) as pool:
            pairs = pool.starmap(_load_chunk, chunks)
      return _stack_pairs(pairs)
   if israwchunked(f_in):
      raws = rawchunkfiles(f_in)
      if len(raws) == 1:
         pairs = [_load_rawchunk(raws[0])]
      else:
         with multiprocessing.get_context("fork").Pool(cores) as pool:
            pairs = pool.map(_load_rawchunk, raws)
      return _stack_pairs(pairs)
   logger.debug("loading plain text svm data")
   return load_svmlight_file(f_in, zero_based=True)  # type: ignore


def decompress(f_in: str, keep: bool = True) -> None:
   if not ischunked(f_in):
      logger.warning(f"Trains `{f_in}` are not chunked.  Skipped.")
      return
   logger.info(
      f"Decompressing trains of size {human.humanbytes(size(f_in))} from `{f_in}`.")
   (data, label) = load(f_in)
   dump_svmlight_file(data, label, f_in)
   if not keep:
      for (p, q) in chunkfiles(f_in):
         os.remove(p)
         os.remove(q)
   logger.info(
      f"Trains decompressed to {human.humanbytes(os.path.getsize(f_in))}.")


def link(src: str, dst: str) -> None:
   if ischunked(src):
      for n, (p_src, q_src) in enumerate(chunkfiles(src)):
         (p_dst, q_dst) = chunkpath(dst, n)
         rellink(p_src, p_dst)
         rellink(q_src, q_dst)
   elif israwchunked(src):
      for n, raw in enumerate(rawchunkfiles(src)):
         rellink(raw, rawchunkpath(dst, n))
   else:
      rellink(src, dst)


def merge(f_in1: str, f_in2: str, f_out: str) -> None:
   if israwchunked(f_in1) or israwchunked(f_in2):
      n = 0
      for raw in rawchunkfiles(f_in1):
         rellink(raw, rawchunkpath(f_out, n))
         n += 1
      for raw in rawchunkfiles(f_in2):
         rellink(raw, rawchunkpath(f_out, n))
         n += 1
      logger.info(f"Merged {n} raw chunks into {f_out}.")
      return
   n = 0
   for (p_src, q_src) in chunkfiles(f_in1):
      (p_dst, q_dst) = chunkpath(f_out, n)
      rellink(p_src, p_dst)
      rellink(q_src, q_dst)
      n += 1
   for (p_src, q_src) in chunkfiles(f_in2):
      (p_dst, q_dst) = chunkpath(f_out, n)
      rellink(p_src, p_dst)
      rellink(q_src, q_dst)
      n += 1
   logger.info(f"Merged {n} chunks into {f_out}.")


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
            td.append(i)
         else:
            onepos = True
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
