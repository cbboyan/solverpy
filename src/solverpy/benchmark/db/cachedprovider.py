from typing import TextIO 
import os
import gzip
import logging

from .provider import Provider

logger = logging.getLogger(__name__)


class CachedProvider(Provider):

   def __init__(
      self,
      bid: str,
      sid: str,
      limit: (str | None) = None,
      store_cache: bool = False,
      compress: bool = False,
   ):
      Provider.__init__(self, bid, sid, limit, store_cache)
      self.compress = compress
      logger.debug(f"creating provider {self} for {sid} @ {bid}")
      self.load()

   def __repr__(self) -> str:
      if self.limit:
         return f"{type(self).__name__}({self.bid},{self.sid},{self.limit})"
      else:
         return f"{type(self).__name__}({self.bid},{self.sid})"

   def commit(self) -> None:
      if self.cache is None:
         logger.warning("empty cache commit")
         return
      if self._uptodate:
         logger.debug(f"commit skipped; cache {self} is up-to-date")
         return
      ext = ".gz" if self.compress else ""
      f = f"{self.cachepath()}{ext}"
      logger.debug(f"cache {self} writing {f}")
      os.makedirs(os.path.dirname(f), exist_ok=True)
      ouropen = gzip.open if self.compress else open
      with ouropen(f, "wt") as fw:
         self.cachedump(fw)
      logger.debug(f"cache {self} saved {len(self.cache)} entries")
      self._uptodate = True

   def load(self) -> None:
      if self._uptodate:
         logger.debug(f"loading skipped; cache {self} is up-to-date")
         return
      ext = ".gz" if self.compress else ""
      f = f"{self.cachepath()}{ext}"
      logger.debug(f"cache {self} loading {f}")
      if os.path.isfile(f):
         ouropen = gzip.open if self.compress else open
         with ouropen(f, "rt") as fr:
            self.cacheload(fr)
         logger.debug(f"cache {self} loaded {len(self.cache)} entries")
      else:
         self.cache = {}
         logger.debug(f"cache {self} not found {f}")
      self._uptodate = True

   def cachepath(self) -> str:
      raise NotImplementedError()

   def cachedump(self, fw: TextIO) -> None:
      del fw
      raise NotImplementedError()

   def cacheload(self, fr: TextIO) -> None:
      del fr
      raise NotImplementedError()

