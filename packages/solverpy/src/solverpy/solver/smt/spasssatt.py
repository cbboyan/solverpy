from typing import TYPE_CHECKING

from ..shellsolver import ShellSolver
from ..plugins.status.smt import Smt
from ..plugins.shell.time import Time

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import Result

SPASSSATT_BINARY = "SPASS-SATT"

# Nothing is passed unconditionally.  SPASS-SATT prints no banner and, with
# no flags, no statistics either; see `process` below.
SPASSSATT_STATIC = ""


class SpassSatt(ShellSolver):
   """
   The `SPASS-SATT` CDCL(LA) solver for linear rational and linear
   mixed/integer arithmetic (QF_LRA, QF_LIA, QF_LIRA).

   The strategy (sid) supplies SPASS-SATT's command-line options, as for
   [`Opensmt`][solverpy.solver.smt.opensmt.Opensmt]. An empty sid means
   SPASS-SATT's own defaults.

   SPASS-SATT has no time or memory limit options of its own, so the limit
   is enforced by the shell `timeout` wrapper and the memory plugin. It also
   reads only from a file argument, not stdin.
   """

   _binary = SPASSSATT_BINARY

   def __init__(
      self,
      limit: str,
      binary: str = SPASSSATT_BINARY,
      static: str = SPASSSATT_STATIC,
      plugins: list["Plugin"] = [],
      complete: bool = True,
   ):
      plugins = plugins + [
         Time(),
         Smt(complete=complete),
      ]
      ShellSolver.__init__(
         self,
         f"{binary} {static}".rstrip(),
         limit,
         plugins=plugins,
         wait=1,
         binary=binary,
      )

   def process(self, output: str) -> "Result":
      # With no flags, SPASS-SATT emits no statistics: `status` comes from
      # the Smt plugin (SPASS-SATT prints `sat` or `unsat` on its own line)
      # and `runtime` from Time. `-t`/`-S` add timing and LA-statistics
      # blocks, but their format is a multi-section dump (sharing stats, SAT
      # solver stats, simplex stats, branch-and-bound stats, phase timings)
      # rather than flat key/value lines, so it is not parsed here.
      del output  # no statistics parsed
      return {}
