from typing import TYPE_CHECKING

from ..shellsolver import ShellSolver
from ..plugins.status.smt import Smt
from ..plugins.shell.time import Time

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import Result

OPENSMT_BINARY = "opensmt"

# Nothing is passed unconditionally.  opensmt has no `--quiet` (it prints no
# banner) and no statistics flag; see `process` below.
OPENSMT_STATIC = ""


class Opensmt(ShellSolver):
   """
   The `opensmt` SMT solver.

   The strategy (sid) supplies opensmt's command-line options, as for
   [`Primo`][solverpy.solver.smt.primo.Primo] and
   [`Llm2smt`][solverpy.solver.smt.llm2smt.Llm2smt].  An empty sid means
   opensmt's own defaults.

   opensmt has no time or memory limit options of its own, so the limit is
   enforced by the shell `timeout` wrapper and the memory plugin.
   """

   _binary = OPENSMT_BINARY

   def __init__(
      self,
      limit: str,
      binary: str = OPENSMT_BINARY,
      static: str = OPENSMT_STATIC,
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
      # A release opensmt emits no statistics, so there is nothing to parse:
      # `status` comes from the Smt plugin (opensmt prints `sat`, `unsat` or
      # `unknown` on its own line) and `runtime` from Time.
      #
      # Statistics exist in the sources but are compiled out.  They are behind
      # the `STATISTICS` cmake option, which defaults to OFF, and only then do
      # `(set-option :produce-stats 1)` and the `; Label....: value` dumps in
      # CoreSMTSolver/TSolver/Egraph do anything.  Enabling it would need a
      # section-aware parser rather than a flat one, because each solver
      # repeats the same labels under its own `; STATISTICS FOR <name>`
      # heading.  `-v` is not a substitute: it traces restart progress to
      # stderr during the search rather than reporting final counters.
      del output  # no statistics in a release build
      return {}
