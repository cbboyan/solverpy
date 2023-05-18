import os
import logging

from .provider import Provider

logger = logging.getLogger(__name__)

class CachedProvider(Provider):

   def __init__(self, bid, sid, limit=None):
      Provider.__init__(self, bid, sid, limit)
      logger.debug(f"creating provider {self} for {sid} @ {bid}")
      self.load()

   def __repr__(self):
      if self.limit:
         return f"{type(self).__name__}({self.bid},{self.sid},{self.limit})"
      else:
         return f"{type(self).__name__}({self.bid},{self.sid})"

   def commit(self):
      if self.cache is None:
         logger.warning("empty cache commit")
         return
      f = self.cachepath()
      logger.debug(f"cache {self} writing {f}")
      os.makedirs(os.path.dirname(f), exist_ok=True)
      with open(f,"w") as fw:
         self.cachedump(fw)
      logger.debug(f"cache {self} saved {len(self.cache)} entries")
   
   def load(self):
      f = self.cachepath()
      logger.debug(f"cache {self} loading {f}")
      if os.path.isfile(f):
         with open(f) as fr:
            self.cacheload(fr)
         logger.debug(f"cache {self} loaded {len(self.cache)} entries")
      else:
         self.cache = {}
         logger.debug(f"cache {self} not found {f}")

   def cachepath(self):
      raise NotImlementedError()

   def cachedump(self, fw):
      raise NotImlementedError()

   def cacheload(self, fr):
      raise NotImlementedError()

