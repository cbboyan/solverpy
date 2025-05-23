from typing import Pattern, TYPE_CHECKING
import re

from ..smtsolver import SmtSolver
from ...tools import patterns, human

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import Builder, Result

Z3_BINARY = "z3"

Z3_STATIC: str = "-smt2 -st"

Z3_BUILDER: "Builder" = {
   "T": "-T:%s",
   "M": lambda x: f"-memory:{int(1024*float(x))}",
}

Z3_PAT: Pattern = re.compile(
   r"^.:([a-z-]*)\s*([0-9.]*)",
   flags=re.MULTILINE,
)

Z3_MEMOUT: Pattern = re.compile(
   r'error "out of memory"',
   flags=re.MULTILINE,
)


class Z3(SmtSolver):

   def __init__(
      self,
      limit: str,
      binary: str = Z3_BINARY,
      static: str = Z3_STATIC,
      plugins: list["Plugin"] = [],
   ):
      cmd = f"{binary} {static}"
      SmtSolver.__init__(
         self,
         cmd,
         limit,
         Z3_BUILDER,
         plugins,
         1,
      )

   def process(self, output: str) -> "Result":
      result = patterns.keyval(Z3_PAT, output)
      result = patterns.mapval(result, human.numeric)
      if re.search(Z3_MEMOUT, output):
         result["status"] = "memout"
      return result
