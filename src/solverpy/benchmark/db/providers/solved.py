import os
import logging

from ..cachedprovider import CachedProvider
from ...path import bids, sids

logger = logging.getLogger(__name__)

NAME = "solved"
   
def delfix(problem : str, fix : (str|int|None)) -> str:
   """Delete a prefix of a problem name."""
   if not fix: # covers None, 0, "" (also False)
      return problem
   if (type(fix) is str) and problem.startswith(fix):
      return problem[len(fix):]
   if (type(fix) is int) and problem.count("/") >= fix:
      parts = problem.split("/")
      return "/".join(parts[fix:])
   logger.warning(f"Uknown delfix value type {type(fix)} of '{fix}'")
   return problem
      
class Solved(CachedProvider):

   def __init__(self, bid, sid, limit, store_cached=True, delfix=None):
      CachedProvider.__init__(self, bid, sid, limit, store_cached)
      self._delfix = delfix

   def store(self, task, result):
      if task.solver.solved(result):
         problem = delfix(task.problem, self._delfix)
         if problem not in self.cache:
            self.cache.add(problem)
            self._uptodate = False

   def load(self):
      super().load()
      if not self.cache:
         self.cache = set()

   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid, limit=self.limit),
         sids.name(self.sid)).rstrip("/") 

   def cacheload(self, fr):
      self.cache = set(x for x in fr.read().strip().split("\n") if x)

   def cachedump(self, fw):
      if self.cache:
         fw.write("\n".join(sorted(self.cache))+"\n")


