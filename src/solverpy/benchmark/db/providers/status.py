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
         val = result["status"]
         if (task.problem not in self.cache) or (self.cache[task.problem] != val):
            self.cache[task.problem] = val
            self._uptodate = False
   
   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid, limit=self.limit),
         sids.name(self.sid)).rstrip("/") 

   def cacheload(self, fr):
      def split(line):
         i = line.rindex(DELIM)
         return (line[:i], line[i+len(DELIM):])
      lines = fr.read().strip().split("\n")
      self.cache = dict(split(line) for line in lines if line)

   def cachedump(self, fw):
      if self.cache:
         fw.write("\n".join(f"{p}{DELIM}{self.cache[p]}" for p in sorted(self.cache))+"\n")

