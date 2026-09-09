from typing import TYPE_CHECKING
import re

from ..shellsolver import ShellSolver
from ...tools import patterns, human
from ..plugins.status.tptp import Tptp
from ..plugins.shell.time import Time

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import LimitBuilder, Result

V_BINARY = "vampire"

V_STATIC = "--proof tptp -stat full --input_syntax tptp --memory_limit 2048 --output_axiom_names on"

V_BUILDER: "LimitBuilder" = {
   "T": "--time_limit %ss",
   "M": "--memory_limit %s",
}

V_PAT = re.compile(r"^% (.*): ([0-9.]*).*$", re.MULTILINE)

V_TABLE = {
   "Active clauses": "Active",
   "Passive clauses": "Passive",
   "Generated clauses": "Generated",
   "Initial clauses   ": "Initial",
   "Time elapsed": "Runtime",
   "Memory used [KB]": "Memory",
   "Split clauses": "Splits",
}


class Vampire(ShellSolver):
   """
   The `vampire` automated theorem prover for first-order logic.

   The strategy (sid) supplies Vampire's command-line options, appended
   after the static options. Output includes a TPTP proof and a `--stat
   full` statistics block, parsed by
   [`process`][solverpy.solver.atp.vampire.Vampire.process]. Status is
   decided by the [`Tptp`][solverpy.solver.plugins.status.tptp.Tptp] plugin
   from the TSTP `SZS status` line.
   """

   _binary = V_BINARY

   def __init__(
      self,
      limit: str,
      binary: str = V_BINARY,
      static: str = V_STATIC,
      complete: bool = True,
      plugins: list["Plugin"] = [],
   ):
      cmd = f"{binary} {static}"
      plugins = plugins + [
         Time(),
         Tptp(complete=complete),
      ]
      ShellSolver.__init__(
         self,
         cmd,
         limit,
         V_BUILDER,
         plugins,
         1,
         complete,
         binary=binary,
      )

   def process(self, output: str) -> "Result":
      """Parse Vampire's `--stat full` statistics block into a result dict."""
      result = patterns.keyval(V_PAT, output, V_TABLE)
      result = patterns.mapval(result, human.numeric)
      return result

