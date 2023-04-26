import os

from ..cachedprovider import CachedProvider
from ....path import bids

NAME = "status"

class Status(CachedProvider):
   
   def __init__(self, bid, sid):
      CachedProvider.__init__(self, bid, sid)
   
   def query(self, instance, strategy):
      return None

   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid, self.solver.limits.limit),
         self.sid).rstrip("/")

   def cachedump(self, f):
      status = ["%s:%s" % (p, r["status"]) for (p,r) in self.cache.items() 
                if "status" in r]
      status.sort()
      status = "\n".join(status) + ("\n" if status else "")
      with open(f,"w") as fw: fw.write(status)

   def cacheload(self, f):
      if not os.path.isfile(f): 
         return {}
      solved = open(f).read().strip()
      if not solved:
         return {}
      solved = solved.split("\n")
      solved = dict(x.rsplit(":",1) for x in solved)
      return {x:dict(status=y) for (x,y) in solved.items()}

