from typing import Any, TextIO, TYPE_CHECKING
import os
import logging

from ..cachedprovider import CachedProvider
from ...path import bids, sids

if TYPE_CHECKING:
   from ....task.solvertask import SolverTask

logger = logging.getLogger(__name__)

NAME = "solved"


class Solved(CachedProvider):

   def __init__(
      self,
      bid: str,
      sid: str,
      limit: str,
      store_cached: bool = True,
      delfix: (str | int | None) = None,
   ):
      CachedProvider.__init__(
         self,
         bid,
         sid,
         limit,
         store_cached,
      )
      self._delfix = delfix

   def store(
      self,
      task: "SolverTask",
      result: dict[str, Any],
   ) -> None:
      if task.solver.solved(result):
         problem = delfix(task.problem, self._delfix)
         if problem not in self.cache:
            self.cache.add(problem)
            self._uptodate = False

   def load(self) -> None:
      super().load()
      if not self.cache:
         self.cache = set()

   def cachepath(self) -> str:
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid, limit=self.limit),
         sids.name(self.sid),
      ).rstrip("/")

   def cacheload(self, fr: TextIO) -> None:
      self.cache = set(x for x in fr.read().strip().split("\n") if x)

   def cachedump(self, fw: TextIO) -> None:
      if self.cache:
         fw.write("\n".join(sorted(self.cache)) + "\n")


def delfix(
      problem: str,
      fix: (str | int | None),
) -> str:
   """Delete a prefix of a problem name."""
   if not fix:  # covers None, 0, "" (also False)
      return problem
   if (type(fix) is str) and problem.startswith(fix):
      return problem[len(fix):]
   if (type(fix) is int) and problem.count("/") >= fix:
      parts = problem.split("/")
      return "/".join(parts[fix:])
   logger.warning(f"Uknown delfix value type {type(fix)} of '{fix}'")
   return problem

