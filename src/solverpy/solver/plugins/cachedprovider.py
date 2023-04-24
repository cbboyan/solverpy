import os
from multiprocessing import Manager

from .provider import Provider

class CachedProvider(Provider):

   def __init__(self, bid, sid):
      self.bid = bid
      self.sid = sid
      man = Manager()
      self.cache = None
      self.results = man.list() # shared list 

   def register(self, solver):
      solver.providers.append(self)
      self.solver = solver
      self.cache = self.load() # thread-local copy / not synced

   def reset(self, bid, sid):
      self.flush()
      self.bid = bid
      self.sid = sid
      self.cache = self.load()
   
   def query(self, instance, strategy):
      (bid, p) = instance
      if not self.check(bid, strategy):
         raise Exception("Error: Query on invalid bid/sid in CachedProvider.")
      return self.cache[p] if p in self.cache else None

   def store(self, instance, strategy, output, result):
      if not self.solver.valid(result):
         return
      (bid, p) = instance
      if not self.check(bid, strategy):
         raise Exception("Error: Store on invalid bid/sid in CachedProvider.")
      self.results.append((p, result))

   def check(self, bid, sid):
      return (self.bid == bid) and (self.sid == sid)

   def flush(self):
      if self.cache is None:
         return
      self.cache.update(dict(self.results))
      while self.results:
         self.results.pop()
      f = self.cachepath()
      os.makedirs(os.path.dirname(f), exist_ok=True)
      self.cachedump(f)

   def load(self):
      f = self.cachepath()
      return self.cacheload(f)

   def cachedump(self, f):
      raise NotImlementedError()

   def cacheload(self, f):
      raise NotImlementedError

