from typing import Pattern, TYPE_CHECKING
import re

from ..shellsolver import ShellSolver
from ..plugins.status.smt import Smt
from ..plugins.shell.time import Time
from ...tools import human, patterns

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import Result

# The SMT-LIB2 front end, not the plain `yices` binary: `yices` reads the
# Yices native language and rejects an SMT-LIB2 file with a syntax error on
# `set-logic`.
YICES_BINARY = "yices-smt2"

YICES_STATIC = "--stats"

# `--stats` writes the statistics to stdout after the last command, as a
# parenthesized block of ` :key value` lines.  Keys are lowercase; the core
# ones use `-` separators (`:clause-db-reduce`), the MCSat ones add `::`, `_`
# and `.` (`:mcsat::bv::explain::full_bv_sat.propagation`).  Values are
# unsigned counters or fixed-point reals (`:total-run-time 0.022`,
# `:mem-usage 4.758`).  There is no banner to suppress at the default
# verbosity, so `--stats` is the whole static command line.
YICES_STATS: Pattern = re.compile(
   r"^\s*:([a-z][a-z0-9_.:-]*)\s+([0-9]+(?:\.[0-9]+)?)\s*$",
   flags=re.MULTILINE,
)


class Yices(ShellSolver):
   """
   The `yices-smt2` SMT solver (Yices 2).

   The strategy (sid) supplies yices' command-line options, appended after
   the static options, as for [`Primo`][solverpy.solver.smt.primo.Primo].

   yices does have a `--timeout=<seconds>` option, but it is deliberately
   unused, so the limit is left to the shell `timeout` wrapper as for
   [`Primo`][solverpy.solver.smt.primo.Primo].  On its own timeout yices
   answers `unknown` and exits 0, which at the default verbosity is
   indistinguishable from a genuine `unknown` -- the `(check-sat:
   interrupted)` marker appears only at `-v 2`, which also floods the output
   with a line per restart.  `unknown` counts as a failure and not as a
   timeout for [`Smt`][solverpy.solver.plugins.status.smt.Smt], so such a
   result would never be recomputed at a longer cutoff.  Letting `timeout`
   kill yices instead yields exit code 124 and the correct `TIMEOUT` status,
   at the cost of the statistics of runs that time out.

   yices has no memory limit option either; that is the memory plugin's job.
   """

   _binary = YICES_BINARY

   def __init__(
      self,
      limit: str,
      binary: str = YICES_BINARY,
      static: str = YICES_STATIC,
      plugins: list["Plugin"] = [],
      complete: bool = True,
   ):
      plugins = plugins + [
         Time(),
         Smt(complete=complete),
      ]
      ShellSolver.__init__(
         self,
         f"{binary} {static}",
         limit,
         plugins=plugins,
         wait=1,
         binary=binary,
      )

   def process(self, output: str) -> "Result":
      result = patterns.keyval(YICES_STATS, output)
      result = patterns.mapval(result, human.numeric)
      # Drop the zero counters, as for `Primo`.  Zero and absent already mean
      # the same thing here: yices prints only the counters of the solver
      # components it built, so a QF_AUFBV run reports four keys and no
      # `simplex-*` or `egraph-*` family at all, and a missing key had to be
      # read as zero anyway.  It saves the most under `--mcsat`, which emits
      # over sixty keys of which almost all stay zero.
      return {key: val for (key, val) in result.items() if val != 0}
