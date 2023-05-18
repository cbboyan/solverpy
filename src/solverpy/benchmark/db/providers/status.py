import os
import logging

from ..cachedprovider import CachedProvider
from ...path import bids

logger = logging.getLogger(__name__)

NAME = "status"

DELIM = "\t"

class Status(CachedProvider):

   def __init__(self, bid, sid, limit):
      CachedProvider.__init__(self, bid, sid, limit)

   def store(self, task, result):
      if task.solver.valid(result):
         self.cache[task.problem] = result["status"]
   
   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid, limit=self.limit),
         self.sid).rstrip("/") 

   def cacheload(self, fr):
      def split(line):
         i = line.rindex(DELIM)
         return (line[:i], line[i+len(DELIM):])
      lines = fr.read().strip().split("\n")
      self.cache = dict(split(line) for line in lines)

   def cachedump(self, fw):
      fw.write("\n".join(f"{p}{DELIM}{self.cache[p]}" for p in sorted(self.cache))+"\n")

