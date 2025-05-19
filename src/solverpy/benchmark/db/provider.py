from typing import Any, Callable, TYPE_CHECKING
from ...solver.object import SolverPyObj

if TYPE_CHECKING:
   from ...task.solvertask import SolverTask

ProviderMaker = Callable[[str, str, str], "Provider"]


class Provider(SolverPyObj):
   """A data provider that stores and/or queries results of tasks."""

   def __init__(
      self,
      bid: str,
      sid: str,
      limit: (str | None) = None,
      store_cached: bool = False,
   ):
      self.bid = bid
      self.sid = sid
      self.limit = limit
      self.store_cached = store_cached
      self._uptodate = False
      "call store for cached results."

   @classmethod
   def Maker(cls, **kwargs) -> ProviderMaker:

      class MakerMaker(SolverPyObj):

         def __init__(self):
            SolverPyObj.__init__(
               self,
               cls_name = cls.__name__,
               **kwargs,
            )

         def __call__(
            self,
            bid: str,
            sid: str,
            limit: (str | None) = None,
         ):
            return cls(bid, sid, limit, **kwargs)

      return MakerMaker()

   def query(
      self,
      task: "SolverTask",
   ) -> (dict[str, Any] | None):
      """Return the cached result for `task` or None if not available."""
      del task  # unused argument
      return None

   def store(
      self,
      task: "SolverTask",
      result: dict[str, Any],
   ):
      """New result for `task` was found.  Update the cache."""
      del task, result  # unused arguments
      pass

   def cached(
      self,
      task: "SolverTask",
      result: dict[str, Any],
   ):
      """Announcement that the cached `result` for `task` was found."""
      if self.store_cached:
         self.store(task, result)

   def commit(self) -> None:
      """Save/flush the data."""
      pass

   def check(self, task: "SolverTask") -> None:
      if (self.bid != task.bid) or (self.sid != task.sid):
         raise Exception("Error: Operation on invalid bid/sid in a provider.")

