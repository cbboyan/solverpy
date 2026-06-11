from typing import Any, TYPE_CHECKING
import os
import glob
import io
import json
import logging
import multiprocessing
from collections import defaultdict

from solverpy.tools import human
from solverpy.tools.external import external
from .plugins.trains import rellink

if TYPE_CHECKING:
   from scipy.sparse import spmatrix, csr_matrix
   from numpy import ndarray

logger = logging.getLogger(__name__)


def chunk_path(f_in: str, n: int) -> tuple[str, str]:
   return (f"{f_in}-chunk{n:04d}-data.npz", f"{f_in}-chunk{n:04d}-label.npz")


def chunk_files(f_in: str) -> list[tuple[str, str]]:
   paths = sorted(glob.glob(f"{f_in}-chunk*-data.npz"))
   suffix = "-data.npz"
   return [(p, p[:-len(suffix)] + "-label.npz") for p in paths]


def chunk_exists(f_in: str) -> bool:
   return len(chunk_files(f_in)) > 0


def _chunk_save(data: "spmatrix", label: "ndarray", f_in: str, n: int) -> None:
   import numpy
   import scipy.sparse
   (z_data, z_label) = chunk_path(f_in, n)
   d_out = os.path.dirname(z_data)
   if d_out:
      os.makedirs(d_out, exist_ok=True)
   scipy.sparse.save_npz(z_data, data, compressed=True)
   numpy.savez_compressed(z_label, label=label)
   logger.debug(f"saved chunk {n}: {z_data}")


def _chunk_compress(lines: list[str], f_in: str, n: int) -> None:
   from sklearn.datasets import load_svmlight_file
   buf = io.BytesIO("".join(lines).encode())
   (data, label) = load_svmlight_file(buf, zero_based=True)  # type: ignore
   _chunk_save(data, label, f_in, n)


def _chunk_load(p: str, q: str) -> tuple["csr_matrix", "ndarray"]:
   import numpy
   import scipy.sparse
   return (scipy.sparse.load_npz(p), numpy.load(q, allow_pickle=True)["label"])


def _chunk_stack(
   pairs: list[tuple["csr_matrix",
                     "ndarray"]]) -> tuple["spmatrix", "ndarray"]:
   import numpy
   import scipy.sparse
   datas = [d for (d, _) in pairs]
   labels = [lbl for (_, lbl) in pairs]
   shapes: list[tuple[int, int]] = []
   for d in datas:
      assert d.shape is not None
      shapes.append(d.shape)
   max_cols = max(s[1] for s in shapes)
   normalized = [
      scipy.sparse.csr_matrix(
         (d.data, d.indices,
          d.indptr), shape=(s[0], max_cols)) if s[1] < max_cols else d
      for d, s in zip(datas, shapes)
   ]
   return (scipy.sparse.vstack(normalized), numpy.concatenate(labels))


def raw_path(f_in: str, n: int) -> str:
   return f"{f_in}-raw{n:04d}"


def raw_files(f_in: str) -> list[str]:
   return sorted(glob.glob(f"{f_in}-raw[0-9][0-9][0-9][0-9]"))


def raw_exists(f_in: str) -> bool:
   return len(raw_files(f_in)) > 0


def metadata_path(f_in: str) -> str:
   return f"{f_in}-meta.json"


def metadata_load(f_in: str) -> dict[str, Any]:
   path = metadata_path(f_in)
   if not os.path.isfile(path):
      return {}
   with open(path) as fh:
      return json.load(fh)


def metadata_save(f_in: str, stats: dict[str, Any]) -> None:
   path = metadata_path(f_in)
   directory = os.path.dirname(path)
   if directory:
      os.makedirs(directory, exist_ok=True)
   with open(path, "w") as fh:
      json.dump(stats, fh, indent=2, sort_keys=True)
      fh.write("\n")


def _raw_compress(raw_path: str, f_in: str, n: int) -> None:
   from sklearn.datasets import load_svmlight_file
   with open(raw_path) as fh:
      lines = fh.readlines()
   buf = io.BytesIO("".join(lines).encode())
   (data, label) = load_svmlight_file(buf, zero_based=True)  # type: ignore
   _chunk_save(data, label, f_in, n)
   os.remove(raw_path)


def _raw_load(raw_path: str) -> tuple["csr_matrix", "ndarray"]:
   from sklearn.datasets import load_svmlight_file
   return load_svmlight_file(raw_path, zero_based=True)  # type: ignore


def exists(f_in: str) -> bool:
   return chunk_exists(f_in) or raw_exists(f_in) or os.path.isfile(f_in)


def size(f_in: str) -> int:
   if chunk_exists(f_in):
      return sum(
         os.path.getsize(p) + os.path.getsize(q)
         for (p, q) in chunk_files(f_in))
   if raw_exists(f_in):
      return sum(os.path.getsize(p) for p in raw_files(f_in))
   return os.path.getsize(f_in)


def format(f_in: str) -> str:
   if chunk_exists(f_in):
      return "binary/chunks"
   if raw_exists(f_in):
      return "text/raw-chunks"
   if os.path.isfile(f_in):
      return "text/svm"
   return "unknown"


def storage(f_in: str) -> dict[str, Any]:
   chunks = chunk_files(f_in)
   raws = raw_files(f_in)
   if chunks:
      file_count = 2 * len(chunks)
      chunk_count = len(chunks)
   elif raws:
      file_count = len(raws)
      chunk_count = len(raws)
   elif os.path.isfile(f_in):
      file_count = 1
      chunk_count = 1
   else:
      file_count = 0
      chunk_count = 0
   return {
      "format": format(f_in),
      "stored_bytes": size(f_in) if exists(f_in) else 0,
      "chunks": chunk_count,
      "files": file_count,
   }


@external
def compress(f_in: str,
             keep: bool = False,
             chunk_size: int = 1_000_000,
             cores: int | None = None) -> None:
   if raw_exists(f_in):
      rawcompress(f_in, cores=cores)
      return
   if chunk_exists(f_in):
      logger.warning(f"Trains {f_in} are already chunked.  Skipped.")
      return
   if not os.path.isfile(f_in):
      logger.warning(f"No trains to compress: {f_in}.")
      return
   logger.info(
      f"Compressing trains of size {human.humanbytes(size(f_in))} from `{f_in}`."
   )
   n = 0
   batch: list[str] = []
   with open(f_in) as fh:
      for line in fh:
         batch.append(line)
         if len(batch) >= chunk_size:
            _chunk_compress(batch, f_in, n)
            n += 1
            batch = []
   if batch:
      _chunk_compress(batch, f_in, n)
      n += 1
   if not keep:
      os.remove(f_in)
   logger.info(
      f"Trains compressed to {n} chunks, {human.humanbytes(size(f_in))} total."
   )


def rawcompress(f_in: str, cores: int | None = None) -> None:
   raws = raw_files(f_in)
   if not raws:
      logger.warning(f"No raw chunks found: {f_in}.")
      return
   logger.info(
      f"Compressing {len(raws)} raw chunks of size {human.humanbytes(size(f_in))} from `{f_in}`."
   )
   args = [(raw, f_in, n) for (n, raw) in enumerate(raws)]
   if len(args) == 1:
      _raw_compress(*args[0])
   else:
      with multiprocessing.get_context("fork").Pool(cores) as pool:
         pool.starmap(_raw_compress, args)
   logger.info(
      f"Compressed to {len(raws)} NPZ chunks, {human.humanbytes(size(f_in))} total."
   )


def load(f_in: str, cores: int | None = None) -> tuple["spmatrix", "ndarray"]:
   logger.info(
      f"Loading trains of size {human.humanbytes(size(f_in))} from `{f_in}`.")
   if chunk_exists(f_in):
      chunks = chunk_files(f_in)
      if len(chunks) == 1:
         pairs = [_chunk_load(*chunks[0])]
      else:
         with multiprocessing.get_context("fork").Pool(cores) as pool:
            pairs = pool.starmap(_chunk_load, chunks)
      return _chunk_stack(pairs)
   if raw_exists(f_in):
      raws = raw_files(f_in)
      if len(raws) == 1:
         pairs = [_raw_load(raws[0])]
      else:
         with multiprocessing.get_context("fork").Pool(cores) as pool:
            pairs = pool.map(_raw_load, raws)
      return _chunk_stack(pairs)
   from sklearn.datasets import load_svmlight_file
   logger.debug("loading plain text svm data")
   return load_svmlight_file(f_in, zero_based=True)  # type: ignore


def decompress(f_in: str, keep: bool = True) -> None:
   from sklearn.datasets import dump_svmlight_file
   if not chunk_exists(f_in):
      logger.warning(f"Trains `{f_in}` are not chunked.  Skipped.")
      return
   logger.info(
      f"Decompressing trains of size {human.humanbytes(size(f_in))} from `{f_in}`."
   )
   (data, label) = load(f_in)
   dump_svmlight_file(data, label, f_in)
   if not keep:
      for (p, q) in chunk_files(f_in):
         os.remove(p)
         os.remove(q)
   logger.info(
      f"Trains decompressed to {human.humanbytes(os.path.getsize(f_in))}.")


def save(data: "spmatrix", label: "ndarray", f_in: str) -> None:
   for (p, q) in chunk_files(f_in):
      os.remove(p)
      os.remove(q)
   _chunk_save(data, label, f_in, 0)
   logger.info(f"Saved {data.shape[0]} samples to `{f_in}`.")


def link(src: str, dst: str) -> None:
   if chunk_exists(src):
      for n, (p_src, q_src) in enumerate(chunk_files(src)):
         (p_dst, q_dst) = chunk_path(dst, n)
         rellink(p_src, p_dst)
         rellink(q_src, q_dst)
   elif raw_exists(src):
      for n, raw in enumerate(raw_files(src)):
         rellink(raw, raw_path(dst, n))
   else:
      rellink(src, dst)
   if os.path.isfile(metadata_path(src)):
      rellink(metadata_path(src), metadata_path(dst))


def metadata_merge(f_in1: str, f_in2: str, f_out: str) -> None:
   inputs = [metadata_load(f_in1), metadata_load(f_in2)]
   keys = ("vectors", "positive", "negative", "raw_bytes")
   merged = {
      key: sum(item[key] for item in inputs)
      for key in keys if all(key in item for item in inputs)
   }
   if merged:
      metadata_save(f_out, merged)


def merge(f_in1: str, f_in2: str, f_out: str) -> None:
   if raw_exists(f_in1) or raw_exists(f_in2):
      n = 0
      for raw in raw_files(f_in1):
         rellink(raw, raw_path(f_out, n))
         n += 1
      for raw in raw_files(f_in2):
         rellink(raw, raw_path(f_out, n))
         n += 1
      metadata_merge(f_in1, f_in2, f_out)
      logger.info(f"Merged {n} raw chunks into {f_out}.")
      return
   n = 0
   for (p_src, q_src) in chunk_files(f_in1):
      (p_dst, q_dst) = chunk_path(f_out, n)
      rellink(p_src, p_dst)
      rellink(q_src, q_dst)
      n += 1
   for (p_src, q_src) in chunk_files(f_in2):
      (p_dst, q_dst) = chunk_path(f_out, n)
      rellink(p_src, p_dst)
      rellink(q_src, q_dst)
      n += 1
   metadata_merge(f_in1, f_in2, f_out)
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
