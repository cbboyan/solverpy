import os
import logging

from ..cachedprovider import CachedProvider
from ...path import bids, sids

logger = logging.getLogger(__name__)

NAME = "solved"

class Solved(CachedProvider):

   def __init__(self, bid, sid, limit, store_cached=True):
      CachedProvider.__init__(self, bid, sid, limit, store_cached)

   def store(self, task, result):
      if task.solver.solved(result):
         if task.problem not in self.cache:
            self.cache.add(task.problem)
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

