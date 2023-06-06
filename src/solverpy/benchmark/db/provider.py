
class Provider:

   def __init__(self, bid, sid, limit=None, store_cached=False):
      self.bid = bid
      self.sid = sid
      self.limit = limit
      self.store_cached = store_cached

   def query(self, task):
      return None

   def store(self, task, result):
      pass

   def cached(self, task, result):
      if self.store_cached:
         self.store(task, result)

   def commit(self):
      pass

   def check(self, task):
      if (self.bid != task.bid) or (self.sid != task.sid):
         raise Exception("Error: Operation on invalid bid/sid in a provider.")

