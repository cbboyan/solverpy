from typing import TYPE_CHECKING
import os
import gzip

from ..decorator import Decorator
from ....benchmark.path import bids, sids

if TYPE_CHECKING:
   from ...solverpy import SolverPy

NAME = "outputs"


class Outputs(Decorator):
   """Write raw solver output to `solverpy_db/outputs/` for successful runs.

   Activated in the `finished()` hook — after the result dict is complete —
   so the write only happens when `solver.valid(result)` is `True` (i.e. the
   solver actually solved the problem).

   The output file path is structured as:
   `solverpy_db/outputs/<bid+limit>/<sid>/<problem>` (optionally `.gz`).

   When `flatten=True` (default), forward slashes in the problem path are
   replaced with `_._` to avoid deep directory nesting.
   """

   def __init__(
      self,
      flatten: bool = True,
      compress: bool = True,
      pid: str | None = None,
   ):
      """Args:
         flatten: Replace `/` in problem paths with `_._` so all output files
            live in a single flat directory.  Pass a custom string to use a
            different separator.
         compress: Gzip-compress the written file (appends `.gz` to path).
         pid: Optional plugin id for use with `solver.call()`.
      """
      Decorator.__init__(
         self,
         flatten=flatten,
         compress=compress,
         pid=pid,
      )
      self._path = bids.dbpath(NAME)
      self._flatten = flatten
      self._compress = compress

   def register(self, solver: "SolverPy") -> None:
      """Append to decorators and store a reference to the solver."""
      solver.decorators.append(self)
      self.solver = solver

   def path(
      self,
      instance: tuple[str, str],
      strategy: str,
   ) -> str:
      """Return the output file path (without `.gz` extension)."""
      (bid, problem) = instance
      bs = bids.name(bid, limit=self.solver._limits.limit)
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
      """Write *output* to disk if the plugin is enabled and the run succeeded."""
      if not self._enabled:
         return
      if output and self.solver.valid(result):
         self.write(instance, strategy, output)

   def write(
      self,
      instance: tuple[str, str],
      strategy: str,
      content: str,
   ) -> None:
      """Write *content* to the output file, creating directories as needed."""
      if not self._enabled:
         return
      f = self.path(instance, strategy)
      os.makedirs(os.path.dirname(f), exist_ok=True)
      if self._compress:
         fw = gzip.open(f + ".gz", "wb")
      else:
         fw = open(f, "wb")
      fw.write(content.encode())
      fw.close()
