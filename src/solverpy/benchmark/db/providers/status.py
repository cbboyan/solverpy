import os
import logging

from ..cachedprovider import CachedProvider
from ...path import bids, sids

logger = logging.getLogger(__name__)

NAME = "status"

DELIM = "\t"

class Status(CachedProvider):

   def __init__(self, bid, sid, limit, store_cached=True):
      CachedProvider.__init__(self, bid, sid, limit, store_cached)

   def store(self, task, result):
      if task.solver.valid(result):
         val = (result["status"], f'{result["runtime"]:0.3f}')
         if (task.problem not in self.cache) or (self.cache[task.problem] != val):
            self.cache[task.problem] = val
            self._uptodate = False
   
   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid, limit=self.limit),
         sids.name(self.sid)).rstrip("/") 

   def cacheload(self, fr):
      def entry(line):
          line = line.split(DELIM)
          return (line[0], DELIM.join(line[1:]))
      lines = fr.read().strip().split("\n")
      self.cahce = dict(entry(l) for l in lines if l)

   def cachedump(self, fw):
      def entry(problem):
         return DELIM.join(self.cache[problem])
      if self.cache:
         fw.write("\n".join(f"{p}{DELIM}{entry(p)}" for p in sorted(self.cache))+"\n")

