import os

from ..cachedprovider import CachedProvider
from ....benchmark.path import bids

NAME = "solved"

class Solved(CachedProvider):
   
   def __init__(self):
      CachedProvider.__init__(self)
   
   def query(self, instance, strategy):
      return None

   def cachepath(self):
      assert(self.bid)
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid, self.solver.limits.limit),
         self.sid).rstrip("/")

   def cachedump(self, f):
      solved = [p for (p,r) in self.cache.items() 
                if (r is None or self.solver.solved(r))]
      solved.sort()
      solved = "\n".join(solved) + ("\n" if solved else "")
      with open(f,"w") as fw: fw.write(solved)

   def cacheload(self, f):
      if not os.path.isfile(f): 
         return {}
      solved = open(f).read().strip().split("\n")
      return {x:None for x in solved}

  

