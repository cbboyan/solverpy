from typing import Any, TYPE_CHECKING
import os
import logging
import multiprocessing

from ...solver.plugins.decorator import Decorator
from ...benchmark.path import bids

if TYPE_CHECKING:
   from ...solver.timedsolver import TimedSolver

NAME = "trains"

logger = logging.getLogger(__name__)


class Trains(Decorator):

   def __init__(self, dataname: str, filename: str = "train.in"):
      self._lock = multiprocessing.Manager().Lock()
      self.reset(dataname, filename)

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

   def register(self, solver: "TimedSolver") -> None:
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
      if not samples:
         return
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
      del instance, strategy, samples # unused arguments
      pass

