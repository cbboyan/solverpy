import os

from ..decorator import Decorator
from ....benchmark.path import bids

NAME = "outputs"

class Outputs(Decorator):
   
   def __init__(self, flatten=False):
      self._path = bids.dbpath(NAME)
      self._flatten = flatten
   
   def register(self, solver):
      solver.decorators.append(self)
      self.solver = solver
   
   def path(self, instance, strategy):
      (bid, problem) = instance
      bs = bids.name(bid, limit=self.solver.limit)
      if self._flatten:
         slash = "_._" if (self._flatten is True) else self._flatten
         problem = problem.replace("/", slash)
      p = os.path.join(self._path, bs, strategy, problem)
      return p

   def finished(self, instance, strategy, output, result):
      if output and self.solver.valid(result):
         self.write(instance, strategy, output)
   
   def write(self, instance, strategy, content):
      f = self.path(instance, strategy)
      os.makedirs(os.path.dirname(f), exist_ok=True)
      with open(f,"w") as fw:
         fw.write(content)

