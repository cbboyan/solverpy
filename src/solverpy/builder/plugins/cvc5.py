from typing import Any
import re

from .svm import SvmTrains
from ...solver.plugins.db.outputs import Outputs
from ...benchmark.path import bids

NAME = "trains"

SAMPLES = re.compile(r"^; QUANTIFIER SAMPLES\n(.*)^; END QUANTIFIER SAMPLES",
                     flags=re.MULTILINE | re.DOTALL)


class Cvc5Trains(SvmTrains):

   def __init__(self, dataname: str):
      SvmTrains.__init__(self, dataname)

   def extract(
      self,
      instance: tuple[str, str],
      strategy: str,
      output: str,
      result: dict[str, Any],
   ) -> str:
      del instance, strategy, result  # unused arguments
      return cvc5samples(output)


class Cvc5TrainsDebug(Outputs):

   def __init__(self, flatten: bool = True):
      Outputs.__init__(self, flatten)
      self._path = bids.dbpath(NAME)

   def path(self, instance: tuple[str, str], strategy: str) -> str:
      return super().path(instance, strategy) + ".in"

   def finished(
      self,
      instance: tuple[str, str],
      strategy: str,
      output: str,
      result: dict[str, Any],
   ) -> None:
      if not (output and self.solver.solved(result)):
         return
      samples = cvc5samples(output)
      if samples:
         self.write(instance, strategy, samples)


def cvc5samples(output: str) -> str:
   mo = SAMPLES.search(output)
   if not mo:
      return ""
   samples = mo.group(1).strip().split("\n")
   samples = [x for x in samples if x and not x.startswith(";")]
   samples = "\n".join(samples) + "\n" if samples else ""
   return samples

