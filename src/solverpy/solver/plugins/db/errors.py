import os

from .outputs import Outputs
from ....benchmark.path import bids

NAME = "errors"

class Errors(Outputs):
   
   def __init__(self, flatten=False):
      Outputs.__init__(self, flatten)
      self._path = bids.dbpath(NAME)
   
   def finished(self, instance, strategy, output, result):
      if output and not self.solver.valid(result):
         self.write(instance, strategy, output)

