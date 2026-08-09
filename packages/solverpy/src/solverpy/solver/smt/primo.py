from typing import Pattern, TYPE_CHECKING
import re

from ..shellsolver import ShellSolver
from ..plugins.status.smt import Smt
from ..plugins.shell.time import Time
from ...tools import human, patterns

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import Result

PRIMO_BINARY = "primo"

PRIMO_STATIC = "--quiet --stats"

# `--stats` writes one `:key value` pair per line to stderr, which the shell
# solver merges into the captured output.  Keys are lowercase with `.` and `-`
# separators; every value is a `std::uint64_t` counter, so nothing negative or
# fractional appears.  `--quiet` suppresses the startup banner, which would
# otherwise land in the same stream.
PRIMO_STATS: Pattern = re.compile(
   r"^:([a-z][a-z0-9_.-]*)\s+([0-9]+)\s*$",
   flags=re.MULTILINE,
)


class Primo(ShellSolver):
   """
   The `primo` QF_LRA/QF_UF SMT solver.

   The strategy (sid) supplies primo's command-line options, appended after
   the static options, as for [`Llm2smt`][solverpy.solver.smt.llm2smt.Llm2smt].

   primo has no time or memory limit options of its own, so the limit is
   enforced by the shell `timeout` wrapper and the memory plugin.
   """

   _binary = PRIMO_BINARY

   def __init__(
      self,
      limit: str,
      binary: str = PRIMO_BINARY,
      static: str = PRIMO_STATIC,
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
      result = patterns.keyval(PRIMO_STATS, output)
      result = patterns.mapval(result, human.numeric)
      # primo prints every counter it tracks, most of which are zero for any
      # one instance -- around 86% of the 220 keys on the QF_LRA benchmarks.
      # Zero and absent already mean the same thing here, because primo also
      # omits whole families it never reached (a problem settled during
      # preprocessing emits no `sat.*` or `lra.*` keys at all), so read a
      # missing key as zero.
      return {key: val for (key, val) in result.items() if val != 0}
