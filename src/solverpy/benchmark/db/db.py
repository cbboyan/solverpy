from typing import Any, TYPE_CHECKING
import logging

from ...solver.object import SolverPyObj
from ...benchmark.path import bids

if TYPE_CHECKING:
   from .provider import ProviderMaker
   from .provider import Provider
   from ...task.solvertask import SolverTask
   from ...tools.typing import Result

logger = logging.getLogger(__name__)


class DB(SolverPyObj):

   def __init__(self, providers: list["ProviderMaker"]):
      SolverPyObj.__init__(self)
      self._providers = providers
      self.loaded: dict[tuple[str, str], list["Provider"]] = {}

   def represent(self) -> dict[str, Any]:
      return dict(
         path=bids.dbpath(),
         providers=self._providers,
      )

   def connect(self, bid: str, sid: str, limit: str) -> None:
      if (bid, sid) not in self.loaded:
         logger.debug(f"connecting providers for {sid} @ {bid}")
         insts = [maker(bid, sid, limit) for maker in self._providers]
         self.loaded[(bid, sid)] = insts
         logger.debug(f"connected to {len(insts)} providers")

   def providers(self, task: "SolverTask") -> list["Provider"]:
      return self.loaded[(task.bid, task.sid)]

   def commit(self) -> None:
      for key in self.loaded:
         logger.debug(f"db commit: {key}")
         for provider in self.loaded[key]:
            provider.commit()

   def querytask(
      self,
      task: "SolverTask",
   ) -> "Result | None":
      self.connect(task.bid, task.sid, task.solver._limits.limit)
      for provider in self.providers(task):
         provider.check(task)
         result = provider.query(task)
         if result:
            return result
      return None

   def cachedtask(
      self,
      task: "SolverTask",
      result: "Result",
   ) -> None:
      self.connect(task.bid, task.sid, task.solver._limits.limit)
      for provider in self.providers(task):
         provider.check(task)
         provider.cached(task, result)

   def storetask(
      self,
      task: "SolverTask",
      result: "Result",
   ) -> None:
      self.connect(task.bid, task.sid, task.solver._limits.limit)
      for provider in self.providers(task):
         provider.check(task)
         provider.store(task, result)

   def query(
      self,
      tasks: list["SolverTask"],
   ) -> dict["SolverTask", dict[str, Any]]:
      logger.debug(f"db query on {len(tasks)} tasks")
      results = {}
      for task in tasks:
         result = self.querytask(task)
         if result:
            results[task] = result
      logger.debug(f"announcing {len(results)} cached results")
      for (task, result) in results.items():
         self.cachedtask(task, result)
      logger.debug(f"db query done: {len(results)} tasks already done")
      return results

   def store(
      self,
      tasks: list["SolverTask"],
      results: list["Result"],
   ) -> None:
      logger.debug(f"db store on {len(tasks)} tasks")
      count = 0
      for (task, result) in zip(tasks, results):
         self.storetask(task, result)
         count += 1
      self.commit()
      logger.debug(f"db store done: {count} commits")

