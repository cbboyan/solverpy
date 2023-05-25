import os
import re

from ..db.outputs import Outputs
from ....benchmark.path import bids

NAME = "trains"

SAMPLES = re.compile(r"^; QUANTIFIER SAMPLES\n(.*)^; END QUANTIFIER SAMPLES", flags=re.MULTILINE|re.DOTALL)

class Cvc5Trains(Outputs):
   
   def __init__(self, flatten=False):
      Outputs.__init__(self, flatten)
      self._path = bids.dbpath(NAME)
   
   def path(self, instance, strategy):
      return super().path(instance, strategy) + ".in"

   def finished(self, instance, strategy, output, result):
      if not (output and self.solver.solved(result)):
         return
      mo = SAMPLES.search(output)
      if not mo:
         return
      out = mo.group(1).strip().split("\n")
      out = [x for x in out if x and not x.startswith(";")]
      out = "\n".join(out)+"\n" if out else ""
      if out:
         self.write(instance, strategy, out)

