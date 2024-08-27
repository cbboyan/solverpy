import os
import re

from .svm import SvmTrains
from ...solver.plugins.db.outputs import Outputs
from ...benchmark.path import bids

NAME = "trains"

SEL = re.compile(r"^#SEL# .*$", flags=re.MULTILINE)

TRANS = str.maketrans("", "", "[(:,)]=")

def samples(output):
   vectors = SEL.findall(output)
   vectors = [x[7:] for x in vectors] # NOTE: this also removes the sign [+-]
   if vectors: vectors.append("") # new line at the end
   return "\n".join(vectors) if vectors else ""

def featurepath(features):
   return features.translate(TRANS)

class EnigmaTrains(SvmTrains):
   
   def __init__(self, dataname, features):
      self._features = features
      SvmTrains.__init__(self, dataname)

   def featurepath(self):
      return "sel_" + featurepath(self._features)

   def reset(self, dataname=None, filename="train.in"):
      if dataname:
         dataname = os.path.join(dataname, self.featurepath())
      super().reset(dataname, filename)

   def extract(self, instance, strategy, output, result):
      return samples(output)

class EnigmaTrainsDebug(Outputs):

   def __init__(self, features, flatten=True):
      Outputs.__init__(self, flatten)
      self._path = os.path.join(bids.dbpath(NAME), "debug", "sel_"+featurepath(features))
   
   def path(self, instance, strategy, ext=".in"):
      return super().path(instance, strategy) + ext

   def decorate(self, cmd, instance, strategy):
      enimap = self.path(instance, strategy, ".map")
      buckets = self.path(instance, strategy, ".buckets")
      os.makedirs(os.path.dirname(buckets), exist_ok=True)
      return f"{cmd} --enigmatic-output-map={enimap} --enigmatic-output-buckets={buckets}"

   def finished(self, instance, strategy, output, result):
      if not (output and self.solver.solved(result)):
         return
      vectors = samples(output)
      if samples:
         self.write(instance, strategy, vectors)

