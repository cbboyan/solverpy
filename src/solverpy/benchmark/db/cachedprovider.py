import os
import logging

from .provider import Provider

logger = logging.getLogger(__name__)

class CachedProvider(Provider):

   def __init__(self, bid, sid, limit=None):
      logger.debug(f"creating provider {self} for {sid} @ {bid}")
      Provider.__init__(self, bid, sid, limit)
      self.load()

   def __str__(self):
      return type(self).__name__

   def commit(self):
      if self.cache is None:
         logger.warning("empty cache commit")
         return
      f = self.cachepath()
      logger.debug(f"cache writing {f}")
      os.makedirs(os.path.dirname(f), exist_ok=True)
      with open(f,"w") as fw:
         self.cachedump(fw)
      logger.debug(f"cache saved {len(self.cache)} entries")
   
   def load(self):
      f = self.cachepath()
      logger.debug(f"cache loading {f}")
      if os.path.isfile(f):
         with open(f) as fr:
            self.cacheload(fr)
         logger.debug(f"cache loaded {len(self.cache)} entries")
      else:
         self.cache = {}
         logger.debug(f"cache not found {f}")

   def cachepath(self):
      raise NotImlementedError()

   def cachedump(self, fw):
      raise NotImlementedError()

   def cacheload(self, fr):
      raise NotImlementedError()

