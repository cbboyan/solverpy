import os
import re

from .trains import Trains
from ..db.outputs import Outputs
from ....benchmark.path import bids

NAME = "trains"

SAMPLES = re.compile(r"^; QUANTIFIER SAMPLES\n(.*)^; END QUANTIFIER SAMPLES", flags=re.MULTILINE|re.DOTALL)

def cvc5samples(output):
   mo = SAMPLES.search(output)
   if not mo:
      return
   samples = mo.group(1).strip().split("\n")
   samples = [x for x in samples if x and not x.startswith(";")]
   samples = "\n".join(samples)+"\n" if samples else ""
   return samples


class Cvc5Trains(Trains):
   
   def __init__(self, dataname):
      Trains.__init__(self, dataname)

   def extract(self, instance, strategy, output, result):
      return cvc5samples(output)


class Cvc5TrainsDebug(Outputs):
   
   def __init__(self, flatten=False):
      Outputs.__init__(self, flatten)
      self._path = bids.dbpath(NAME)
   
   def path(self, instance, strategy):
      return super().path(instance, strategy) + ".in"

   def finished(self, instance, strategy, output, result):
      if not (output and self.solver.solved(result)):
         return
      samples = cvc5samples(output)
      if samples:
         self.write(instance, strategy, samples)

