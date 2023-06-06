import os, json
import logging

from ..cachedprovider import CachedProvider
from ...path import bids, sids

logger = logging.getLogger(__name__)

NAME = "results"

class Jsons(CachedProvider):

   def __init__(self, bid, sid, limit=None, store_cached=False):
      CachedProvider.__init__(self, bid, sid, limit, store_cached)

   def query(self, task):
      if task.problem in self.cache:
         result = self.cache[task.problem] 
         return task.solver.simulate(result)
      return None

   def store(self, task, result):
      if task.solver.valid(result):
         self.cache[task.problem] = result

   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid),
         sids.name(self.sid)).rstrip("/") + ".json"

   def cacheload(self, fr):
      self.cache = json.load(fr)

   def cachedump(self, fw):
      json.dump(self.cache, fw, indent=3, sort_keys=True)


class JsonsStore(Jsons):

   def __init__(self, bid, sid, limit=None):
      Jsons.__init__(self, bid, sid, limit, store_cached=True)

