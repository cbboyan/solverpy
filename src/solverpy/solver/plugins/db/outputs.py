from typing import TYPE_CHECKING
import os
import gzip

from ..decorator import Decorator
from ....benchmark.path import bids, sids

if TYPE_CHECKING:
   from ...solverpy import SolverPy

NAME = "outputs"


class Outputs(Decorator):

   def __init__(
      self,
      flatten: bool = True,
      compress: bool = True,
   ):
      Decorator.__init__(self, flatten=flatten, compress=compress)
      self._path = bids.dbpath(NAME)
      self._flatten = flatten
      self._compress = compress

   def register(self, solver: "SolverPy") -> None:
      solver.decorators.append(self)
      self.solver = solver

   def path(
      self,
      instance: tuple[str, str],
      strategy: str,
   ) -> str:
      (bid, problem) = instance
      bs = bids.name(bid, limit=self.solver.limits.limit)
      if self._flatten:
         slash = "_._" if (self._flatten is True) else self._flatten
         problem = problem.replace("/", slash)
      p = os.path.join(self._path, bs, sids.name(strategy), problem)
      return p

   def finished(
      self,
      instance: tuple[str, str],
      strategy: str,
      output: str,
      result: dict,
   ) -> None:
      if output and self.solver.valid(result):
         self.write(instance, strategy, output)

   def write(
      self,
      instance: tuple[str, str],
      strategy: str,
      content: str,
   ) -> None:
      f = self.path(instance, strategy)
      os.makedirs(os.path.dirname(f), exist_ok=True)
      if self._compress:
         fw = gzip.open(f + ".gz", "wb")
      else:
         fw = open(f, "wb")
      fw.write(content.encode())
      fw.close()

