
class Provider:
   """A data provider that stores and/or queries results of tasks."""

   def __init__(self, bid, sid, limit=None, store_cached=False):
      self.bid = bid
      self.sid = sid
      self.limit = limit
      self.store_cached = store_cached
      self._uptodate = False
      "call store for cached results."

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

