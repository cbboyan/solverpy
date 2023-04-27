import os

from ..provider import Provider
from ....benchmark.path import bids

NAME = "outputs"

class Outputs(Provider):
   
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
      f = self.path(instance, strategy)
      #print("QUERY", instance, strategy, f)
      if not os.path.isfile(f):
         return None
      output = open(f).read()
      result = self.solver.process(output)
      self.solver.update(instance, strategy, output, result)
      return result

   def store(self, instance, strategy, output, result):
      if not output:
         return
      #print("STORE", instance, strategy, result)
      if self.solver.valid(result):
         f = self.path(instance, strategy)
         os.makedirs(os.path.dirname(f), exist_ok=True)
         open(f,"w").write(output)

