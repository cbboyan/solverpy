from typing import Any, TYPE_CHECKING
import os
import random
import logging
from types import SimpleNamespace

from .. import svm
from .trains import Trains

if TYPE_CHECKING:
   from multiprocessing.managers import SyncManager

logger = logging.getLogger(__name__)


class SvmTrains(Trains):

   def __init__(
      self,
      dataname: str,
      filename: str = "train.in",
      chunk_size: int = 1_000_000,
      **kwargs: Any,
   ):
      Trains.__init__(self,
                      dataname,
                      filename=filename,
                      chunk_size=chunk_size,
                      **kwargs)
      self.info = SimpleNamespace(
         total=0,
         pos=0,
         neg=0,
         line_count=0,
         raw_chunk_n=0,
         chunk_size=chunk_size,
      )

   def connect(self, manager: "SyncManager") -> None:
      """Move local statistics into a namespace owned by the session Manager."""
      if self._lock is not None:
         return
      local = self.info
      super().connect(manager)
      self.info = manager.Namespace()
      self.info.total = local.total
      self.info.pos = local.pos
      self.info.neg = local.neg
      self.info.line_count = local.line_count
      self.info.raw_chunk_n = local.raw_chunk_n
      self.info.chunk_size = local.chunk_size

   def disconnect(self) -> None:
      """Copy shared statistics locally before discarding Manager proxies."""
      if self._lock is None:
         return
      shared = self.info
      self.info = SimpleNamespace(
         total=shared.total,
         pos=shared.pos,
         neg=shared.neg,
         line_count=shared.line_count,
         raw_chunk_n=shared.raw_chunk_n,
         chunk_size=shared.chunk_size,
      )
      super().disconnect()

   def represent(self) -> dict[str, Any]:
      return dict(
         cls=f"{self.__class__.__module__}.{self.__class__.__name__}",
         dataname=self._dataname,
         filename=self._filename,
         chunk_size=self.info.chunk_size,
      )

   def reset(
      self,
      dataname: (str | None) = None,
      filename: str = "train.in",
   ) -> None:
      super().reset(dataname=dataname, filename=filename)
      if hasattr(self, "info"):
         self.info.total = 0
         self.info.pos = 0
         self.info.neg = 0
         self.info.line_count = 0
         self.info.raw_chunk_n = 0

   def exists(self) -> bool:
      return svm.exists(self.path())

   def stats(
      self,
      instance: tuple[str, str],
      strategy: str,
      samples: str,
   ) -> None:
      count = samples.count("\n")
      s0 = samples[0]
      pos = samples.count("\n1 ") + (1 if s0 == "1" else 0)
      neg = samples.count("\n0 ") + (1 if s0 == "0" else 0)
      self.info.total += count
      self.info.pos += pos
      self.info.neg += neg
      with open(self.path() + "-stats.txt", "a") as infa:
         infa.write(f"{instance} {strategy}: {count} ({pos} / {neg})\n")

   def save(
      self,
      instance: tuple[str, str],
      strategy: str,
      samples: str,
   ) -> None:
      if (not samples) or (not self._enabled):
         return
      new_lines = samples.count("\n")
      if self._lock is None:
         raise RuntimeError("SvmTrains must be connected before evaluation")
      self._lock.acquire()
      try:
         if self.info.line_count + new_lines > self.info.chunk_size and \
            self.info.line_count > 0:
            self.info.raw_chunk_n += 1
            self.info.line_count = 0
         raw_path = svm.raw_path(self.path(), self.info.raw_chunk_n)
         os.makedirs(os.path.dirname(self.path()), exist_ok=True)
         with open(raw_path, "a") as fa:
            fa.write(samples)
         self.info.line_count += new_lines
         self.stats(instance, strategy, samples)
      finally:
         self._lock.release()

   def compress(self,
                chunk_size: int | None = None,
                cores: int | None = None) -> None:
      logger.info(
         f"Training vectors count: {self.info.total} ({self.info.pos} / {self.info.neg}) "
      )
      svm.compress(self.path(),
                   chunk_size=chunk_size or self.info.chunk_size,
                   cores=cores)

   def train_data_snapshot(self) -> None:
      """Persist counts and uncompressed bytes for the current logical file."""
      path = self.path()
      if not svm.exists(path):
         return
      metadata = svm.metadata_load(path)
      if svm.format(path).startswith("text/"):
         raw_bytes = svm.size(path)
      else:
         raw_bytes = metadata.get("raw_bytes")
      if self.info.total or "vectors" not in metadata:
         metadata.update({
            "vectors": self.info.total,
            "positive": self.info.pos,
            "negative": self.info.neg,
         })
      if raw_bytes is not None:
         metadata["raw_bytes"] = raw_bytes
      svm.metadata_save(path, metadata)

   def train_data_stats(
      self,
      dataset: str,
      path: str | None = None,
   ) -> dict[str, Any] | None:
      """Return report-ready statistics without loading vector data."""
      path = path or self.path()
      if not svm.exists(path):
         return None
      storage = svm.storage(path)
      metadata = svm.metadata_load(path)
      if "raw_bytes" not in metadata and storage["format"].startswith("text/"):
         metadata["raw_bytes"] = storage["stored_bytes"]
      return {
         "dataset": dataset,
         "path": path,
         **metadata,
         **storage,
      }

   def merge(
      self,
      previous: str | tuple[str, ...],
      outfilename: str,
   ) -> None:
      assert self._filename != outfilename
      assert type(previous) is str
      if not svm.exists(self.path()):
         logger.warning(f"Trains not found: {self.path()}.")
         return
      f_out = self.path(filename=outfilename)
      svm.merge(previous, self.path(), f_out)
      #self.reset(filename=outfilename)

   def link(self, src: str | tuple[str]):
      assert isinstance(src, str)
      if not svm.exists(src):
         logger.warning(f"Link source not found: {src}.")
         return
      dst = self.path()
      if svm.exists(dst):
         logger.warning(f"Link targed exists: {dst}.")
         return
      svm.link(src, dst)


def filter_posneg(
   samples: list[Any],
   ratio: float,
   seed: int = 0,
) -> list[Any]:
   if ratio == 0:
      return samples
   pos = [x for x in samples if x.startswith("1")]
   neg = [x for x in samples if x.startswith("0")]
   random.seed(seed)
   if (ratio > 0) and (len(pos) * ratio < len(neg)):
      # filter negative samples
      neg = random.sample(neg, int(len(pos) * ratio))
      samples = pos + neg
   if (ratio < 0) and (len(neg) * -ratio < len(pos)):
      # filter positive samples
      pos = random.sample(pos, int(len(neg) * -ratio))
      samples = pos + neg
   return samples
