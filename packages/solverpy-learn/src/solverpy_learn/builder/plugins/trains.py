from typing import Any, TYPE_CHECKING
import os
import logging

from solverpy.solver.plugins.managed import Managed
from solverpy.benchmark.path import bids

if TYPE_CHECKING:
   from multiprocessing.managers import SyncManager
   from solverpy.solver.solverpy import SolverPy

NAME = "trains"

logger = logging.getLogger(__name__)


def rellink(f_src: str, f_dst: str):
   d_dst = os.path.dirname(f_dst)
   os.makedirs(d_dst, exist_ok=True)
   rel = os.path.relpath(os.path.realpath(f_src), os.path.realpath(d_dst))
   logger.debug(f"linking {f_src} to {f_dst} via {rel}")
   os.symlink(rel, f_dst)


class Trains(Managed):

   def __init__(self, dataname: str, filename: str = "train.in", **kwargs: Any):
      Managed.__init__(
         self,
         pid="trains",
         dataname=dataname,
         filename=filename,
         **kwargs,
      )
      self._lock = None
      self._enabled = True
      self.reset(dataname, filename)

   def connect(self, manager: "SyncManager") -> None:
      """Create process-shared state from the session-owned Manager."""
      if self._lock is None:
         self._lock = manager.Lock()

   def disconnect(self) -> None:
      """Discard process-shared proxies before their Manager is shut down."""
      self._lock = None

   def represent(self) -> dict[str, Any]:
      return dict(
         cls=f"{self.__class__.__module__}.{self.__class__.__name__}",
         dataname=self._dataname,
         filename=self._filename,
      )

   def reset(
      self,
      dataname: (str | None) = None,
      filename: str = "train.in",
   ) -> None:
      if dataname:
         self._dataname = dataname
      self._filename = filename

   def path(
      self,
      dataname: (str | None) = None,
      filename: (str | None) = None,
   ) -> Any:
      dataname = dataname or self._dataname
      filename = filename or self._filename
      return os.path.join(bids.dbpath(NAME), dataname, filename)

   def exists(self) -> bool:
      return os.path.isfile(self.path())

   def link(self, src: str):
      if not os.path.isfile(src):
         logger.warning(f"Link source not found: {src}.")
         return
      rellink(src, self.path())

   def register(self, solver: "SolverPy") -> None:
      super().register(solver)
      self._solver = solver

   def finished(
      self,
      instance: tuple[str, str],
      strategy: str,
      output: str,
      result: dict[str, Any],
   ):
      if not (output and self._solver.solved(result)):
         return
      samples = self.extract(instance, strategy, output, result)
      self.save(instance, strategy, samples)

   def extract(
      self,
      instance: tuple[str, str],
      strategy: str,
      output: str,
      result: dict[str, Any],
   ) -> Any:
      del instance, strategy, output, result  # unused arguments
      "Extract training samples from `output`."
      raise NotImplementedError()

   def save(
      self,
      instance: tuple[str, str],
      strategy: str,
      samples: str,
   ) -> None:
      if (not samples) or (not self._enabled):
         return
      if self._lock is None:
         raise RuntimeError("Trains must be connected before evaluation")
      self._lock.acquire()
      try:
         os.makedirs(os.path.dirname(self.path()), exist_ok=True)
         with open(self.path(), "a") as fa:
            fa.write(samples)
            self.stats(instance, strategy, samples)
      finally:
         self._lock.release()

   def stats(
      self,
      instance: tuple[str, str],
      strategy: str,
      samples: str,
   ):
      "Save optional statistics."
      del instance, strategy, samples  # unused arguments
      pass
