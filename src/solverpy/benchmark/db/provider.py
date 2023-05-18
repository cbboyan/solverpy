
class Provider:

   def __init__(self, bid, sid, limit=None):
      self.bid = bid
      self.sid = sid
      self.limit = limit

   def query(self, task):
      return None

   def store(self, task, result):
      pass

   def commit(self):
      pass

   def check(self, task):
      if (self.bid != task.bid) or (self.sid != task.sid):
         raise Exception("Error: Operation on invalid bid/sid in a provider.")

