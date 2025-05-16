import os
import logging

from ..cachedprovider import CachedProvider
from ...path import bids, sids
from .solved import delfix

logger = logging.getLogger(__name__)

NAME = "status"

DELIM = "\t"

class Status(CachedProvider):

   def __init__(self, bid, sid, limit, store_cached=True, delfix=None):
      CachedProvider.__init__(self, bid, sid, limit, store_cached)
      self._delfix = delfix
   
   @staticmethod
   def Maker(delfix):
      def maker(bid, sid, limit): 
         return Status(bid, sid, limit, delfix=delfix)
      return maker

   def store(self, task, result):
      if task.solver.valid(result):
         problem = delfix(task.problem, self._delfix)
         val = (result["status"], f'{result["runtime"]:0.3f}')
         if (problem not in self.cache) or (self.cache[problem] != val):
            self.cache[problem] = val
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
      self.cache = dict(entry(l) for l in lines if l)

   def cachedump(self, fw):
      def entry(problem):
         return DELIM.join(self.cache[problem])
      if self.cache:
         fw.write("\n".join(f"{p}{DELIM}{entry(p)}" for p in sorted(self.cache))+"\n")

