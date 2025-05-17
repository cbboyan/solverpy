from ...solver.object import SolverPyObj

class Provider(SolverPyObj):
   """A data provider that stores and/or queries results of tasks."""

   def __init__(self, bid, sid, limit=None, store_cached=False):
      self.bid = bid
      self.sid = sid
      self.limit = limit
      self.store_cached = store_cached
      self._uptodate = False
      "call store for cached results."

   @classmethod
   def Maker(cls, **kwargs):
      class MakerMaker(SolverPyObj):
         def __init__(self):
            SolverPyObj.__init__(self, myname=cls.__name__, **kwargs)
         def __call__(self, bid, sid, limit): 
            return cls(bid, sid, limit, **kwargs)
      return MakerMaker()

   def query(self, task):
      """Return the cached result for `task` or None if not available."""
      return None

   def store(self, task, result):
      """New result for `task` was found.  Update the cache."""
      pass

   def cached(self, task, result):
      """Announcement that the cached `result` for `task` was found."""
      if self.store_cached:
         self.store(task, result)

   def commit(self):
      """Save/flush the data."""
      pass

   def check(self, task):
      if (self.bid != task.bid) or (self.sid != task.sid):
         raise Exception("Error: Operation on invalid bid/sid in a provider.")

