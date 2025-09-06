from typing import Any
import os
import re
import random

from .svm import SvmTrains
from .multi import MultiTrains
from ...solver.plugins.db.outputs import Outputs
from ...benchmark.path import bids

NAME = "trains"

SEL = re.compile(r"^#SEL# .*$", flags=re.MULTILINE)
GEN = re.compile(r"^#GEN# .*$", flags=re.MULTILINE)

TRANS = str.maketrans("", "", "[(:,)]=")


class EnigmaTrains(SvmTrains):

   def __init__(
      self,
      dataname: str,
      features: str,
      variant: str,
      ratio: float = 0,
   ):
      self._features = features
      self._variant = variant
      self._ratio = ratio
      SvmTrains.__init__(self, dataname)

   def featurepath(self) -> str:
      return f"{self._variant}_{featurepath(self._features)}"

   def reset(
      self,
      dataname: (str | None) = None,
      filename: str = "train.in",
   ) -> None:
      if dataname:
         dataname = os.path.join(dataname, self.featurepath())
      super().reset(dataname, filename)

   def extract(
      self,
      instance: tuple[str, str],
      strategy: str,
      output: str,
      result: dict[str, Any],
   ) -> str:
      del instance, strategy, result  # unused arguments
      if not self._enabled:
         return ""
      return samples(output, self._variant, self._ratio)


class EnigmaMultiTrains(MultiTrains):

   def __init__(
      self,
      dataname: str,
      sel: str,
      gen: str,
      ratio: float = 0,
   ):
      MultiTrains.__init__(self, dataname)
      self._sel = EnigmaTrains(dataname, sel, "sel", ratio)
      self._gen = EnigmaTrains(dataname, gen, "gen", ratio)
      assert self._sel.id == self._gen.id == "trains"
      self._id = "trains"
      self.dispatch(self._sel)
      self.dispatch(self._gen)


class EnigmaTrainsDebug(Outputs):

   def __init__(
      self,
      features: str,
      variant: str,
      flatten: bool = True,
      ratio: float = 0,
   ):
      Outputs.__init__(self, flatten)
      self._path = os.path.join(
         bids.dbpath(NAME),
         "debug",
         f"{variant}_{featurepath(features)}",
      )
      self._variant = variant
      self._ratio = ratio

   def path(
      self,
      instance: tuple[str, str],
      strategy: str,
      ext: str = ".in",
   ) -> str:
      return super().path(instance, strategy) + ext

   def decorate(
      self,
      cmd: str,
      instance: tuple[str, str],
      strategy: str,
   ) -> str:
      if self._variant != "sel":
         return cmd
      enimap = self.path(instance, strategy, ".map")
      buckets = self.path(instance, strategy, ".buckets")
      os.makedirs(os.path.dirname(buckets), exist_ok=True)
      return f"{cmd} --enigmatic-output-map={enimap} --enigmatic-output-buckets={buckets}"

   def finished(
      self,
      instance: tuple[str, str],
      strategy: str,
      output: str,
      result: dict[str, Any],
   ) -> None:
      if not (output and self.solver.solved(result)):
         return
      vectors = samples(output, self._variant, self._ratio)
      if vectors:
         self.write(instance, strategy, vectors)


def samples(output: str, variant: str, ratio: float = 0) -> str:
   assert variant in ["sel", "gen"]
   pattern = SEL if variant == "sel" else GEN
   vectors = pattern.findall(output)
   vectors = [x[7:] for x in vectors]  # NOTE: this also removes the sign [+-]
   if ratio != 0:
      pos = [x for x in vectors if x.startswith("1")]
      neg = [x for x in vectors if x.startswith("0")]
      if (ratio > 0) and (len(pos) * ratio < len(neg)):
         # filter negative samples
         neg = random.sample(neg, int(len(pos) * ratio))
         vectors = pos + neg
      if (ratio < 0) and (len(neg) * -ratio < len(pos)):
         # filter positive samples
         pos = random.sample(pos, int(len(neg) * -ratio))
         vectors = pos + neg
   if vectors: vectors.append("")  # new line at the end
   return "\n".join(vectors) if vectors else ""


def featurepath(features: str) -> str:
   return features.translate(TRANS)
