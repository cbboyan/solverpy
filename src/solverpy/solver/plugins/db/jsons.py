import os
import json

from ..cachedprovider import CachedProvider
from ....path import bids

NAME = "results"

class Jsons(CachedProvider):
  
   def __init__(self, bid, sid):
      CachedProvider.__init__(self, bid, sid)

   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid),
         self.sid).rstrip("/") + ".json"

   def cachedump(self, f):
      with open(f,"w") as fw:
         json.dump(self.cache, fw, indent=3, sort_keys=True)

   def cacheload(self, f):
      return json.load(open(f)) if os.path.isfile(f) else {}

