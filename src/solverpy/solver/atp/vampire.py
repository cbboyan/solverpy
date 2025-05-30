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

V_STATIC = "--proof tptp -stat full --input_syntax tptp --memory_limit 2048"

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
      )

   def process(self, output: str) -> "Result":
      result = patterns.keyval(V_PAT, output, V_TABLE)
      result = patterns.mapval(result, human.numeric)
      return result

