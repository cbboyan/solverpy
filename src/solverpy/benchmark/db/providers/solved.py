import os
import logging

from ..cachedprovider import CachedProvider
from ...path import bids

logger = logging.getLogger(__name__)

NAME = "solved"

class Solved(CachedProvider):

   def __init__(self, bid, sid, limit):
      CachedProvider.__init__(self, bid, sid, limit)

   def store(self, task, result):
      if task.solver.solved(result):
         self.cache.add(task.problem)
   
   def load(self):
      super().load()
      if not self.cache:
         self.cache = set()

   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid, limit=self.limit),
         self.sid).rstrip("/") 

   def cacheload(self, fr):
      self.cache = set(fr.read().strip().split("\n"))

   def cachedump(self, fw):
      fw.write("\n".join(sorted(self.cache))+"\n")

