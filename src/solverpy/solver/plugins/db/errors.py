import os

from .outputs import Outputs
from ....benchmark.path import bids

NAME = "errors"

class Errors(Outputs):
   
   def __init__(self):
      self._path = bids.dbpath(NAME)
   
   def finished(self, instance, strategy, output, result):
      if output and not self.solver.valid(result):
         f = self.path(instance, strategy)
         os.makedirs(os.path.dirname(f), exist_ok=True)
         with open(f,"w") as fw:
            fw.write(output)

