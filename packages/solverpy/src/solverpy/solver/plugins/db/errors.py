from typing import TYPE_CHECKING

from .outputs import Outputs
from ....benchmark.path import bids

if TYPE_CHECKING:
   from ....tools.typing import Result

NAME = "errors"


class Errors(Outputs):
   """Write raw solver output to `solverpy_db/errors/` for failed runs.

   Mirror of [`Outputs`][solverpy.solver.plugins.db.outputs.Outputs] with the
   validity check **inverted**: output is written when `solver.valid(result)` is
   `False` (timeouts, errors, unknown results, etc.).

   Useful for debugging — inspect `solverpy_db/errors/` to see what the solver
   printed for problems it could not solve.
   """

   def __init__(
      self,
      flatten: bool = True,
      compress: bool = True,
   ):
      """Args:
         flatten: Replace `/` in problem paths with `_._`.
         compress: Gzip-compress the written file.
      """
      Outputs.__init__(self, flatten, compress)
      self._path: str = bids.dbpath(NAME)

   def finished(
      self,
      instance: tuple[str, str],
      strategy: str,
      output: str,
      result: "Result",
   ) -> None:
      """Write *output* to disk if the run failed (validity check inverted)."""
      if output and not self.solver.valid(result):
         self.write(instance, strategy, output)

