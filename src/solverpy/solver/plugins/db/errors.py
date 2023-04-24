import os

from ..provider import Provider
from ....path import bids

NAME = "errors"

class Errors(Provider):
   
   def __init__(self):
      self._path = bids.dbpath(NAME)

   def register(self, solver):
      solver.providers.append(self)
      self.solver = solver
   
   def path(self, instance, strategy):
      (bid, problem) = instance
      limit = self.solver.limits.limit
      p = os.path.join(self._path, bids.name(bid,limit), strategy, problem)
      return p
   
   def query(self, instance, strategy):
      return None

   def store(self, instance, strategy, output, result):
      #print("STORE", instance, strategy, result)
      if not self.solver.valid(result):
        f = self.path(instance, strategy)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f,"w").write(output)

