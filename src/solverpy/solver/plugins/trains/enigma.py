import re

from .svm import SvmTrains
from ..db.outputs import Outputs
from ....benchmark.path import bids

NAME = "trains"

SEL = re.compile(r"^#SEL# .*$", flags=re.MULTILINE)

def samples(output):
   vectors = SEL.findall(output)
   vectors = [x[7:] for x in vectors] # NOTE: this also removes the sign [+-]
   if vectors: vectors.append("") # new line at the end
   return "\n".join(vectors) if vectors else ""

class EnigmaTrains(SvmTrains):
   
   def __init__(self, dataname, sel_features):
      SvmTrains.__init__(self, dataname)
      self._sel_features = sel_features

   def extract(self, instance, strategy, output, result):
      return samples(output)

class EnigmaTrainsDebug(Outputs):

   def __init__(self, flatten=True):
      Outputs.__init__(self, flatten)
      self._path = bids.dbpath(NAME)
   
   def path(self, instance, strategy, ext=".in"):
      return super().path(instance, strategy) + ext

   def decorate(self, cmd):
      #enimap = self.path(instance, strategy, ".map")
      #buckets = self.path(instance, strategy, ".buckets")
      #return f"{cmd} --enigmatic-output-map={enimap} --enigmatic-output-buckets={buckets}"
      return cmd

   def finished(self, instance, strategy, output, result):
      if not (output and self.solver.solved(result)):
         return
      vectors = samples(output)
      if samples:
         self.write(instance, strategy, vectors)

