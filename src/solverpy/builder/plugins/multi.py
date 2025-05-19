from typing import Any, Callable, TYPE_CHECKING
import logging

from .trains import Trains

if TYPE_CHECKING:
   from ...solver.timedsolver import TimedSolver
   from .svm import SvmTrains

logger = logging.getLogger(__name__)


class MultiTrains(Trains):

   def __init__(self, dataname: str):
      self._trains: list["SvmTrains"] = []
      self._dataname = dataname

   def dispatch(self, t: "SvmTrains"):
      self._trains.append(t)

   def apply(self, function: Callable[["SvmTrains"], None]) -> None:
      for t in self._trains:
         function(t)

   def register(self, solver: "TimedSolver") -> None:
      super().register(solver)
      self._solver = solver
      for t in self._trains:
         t._solver = solver

   def reset(
      self,
      dataname: (str | None) = None,
      filename: str = "train.in",
   ) -> None:
      if dataname:
         self._dataname = dataname
      self.apply(lambda x: x.reset(dataname=dataname, filename=filename))

   def path(
      self,
      dataname: (str | None) = None,
      filename: (str | None) = None,
   ) -> tuple[str, ...]:
      return tuple(t.path(dataname, filename) for t in self._trains)

   def finished(self, *args: Any, **kwargs: Any) -> None:
      self.apply(lambda x: x.finished(*args, **kwargs))

   def extract(self, *args: Any, **kwargs: Any) -> None:
      self.apply(lambda x: x.extract(*args, **kwargs))

   def save(self, *args: Any, **kwargs: Any) -> None:
      self.apply(lambda x: x.save(*args, **kwargs))

   def stats(self, *args: Any, **kwargs: Any) -> None:
      self.apply(lambda x: x.stats(*args, **kwargs))

   def compress(self, *args: Any, **kwargs: Any) -> None:
      self.apply(lambda x: x.compress(*args, **kwargs))

   def merge(self, previous: tuple[str, ...], outfilename: str) -> None:
      assert type(previous) is tuple
      assert len(previous) == len(self._trains)
      for (t0, p0) in zip(self._trains, previous):
         t0.merge(p0, outfilename)

