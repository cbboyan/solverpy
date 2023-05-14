
class Provider:

   def __init__(self, bid, sid):
      self.bid = bid
      self.sid = sid

   def query(self, task):
      return None

   def store(self, task, result):
      pass

   def commit(self):
      pass

