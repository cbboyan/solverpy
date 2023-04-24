import os
import yaml

from ..cachedprovider import CachedProvider
from ....path import bids

NAME = "results"

class Yamls(CachedProvider):
  
   def __init__(self, bid, sid):
      CachedProvider.__init__(self, bid, sid)

   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid),
         self.sid).rstrip("/") + ".yaml"

   def cachedump(self, f):
      with open(f,"w") as fw:
         yaml.dump(self.cache, fw, sort_keys=True)

   def cacheload(self, f):
      return yaml.safe_load(open(f)) if os.path.isfile(f) else {}

