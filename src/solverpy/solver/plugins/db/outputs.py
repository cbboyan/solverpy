import os

from ..decorator import Decorator
from ....benchmark.path import bids

NAME = "outputs"

class Outputs(Decorator):
   
   def __init__(self):
      self._path = bids.dbpath(NAME)
   
   def register(self, solver):
      solver.decorators.append(self)
      self.solver = solver
   
   def path(self, instance, strategy):
      (bid, problem) = instance
      bs = bids.name(bid, limit=self.solver.limits)
      p = os.path.join(self._path, bs, strategy, problem)
      return p

   def finished(self, instance, strategy, output, result):
      if output and self.solver.valid(result):
         f = self.path(instance, strategy)
         os.makedirs(os.path.dirname(f), exist_ok=True)
         with open(f,"w") as fw:
            fw.write(output)

