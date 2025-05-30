from typing import Pattern, TYPE_CHECKING
import re

from ..stdinsolver import StdinSolver
from ..plugins.status.smt import Smt
from ..plugins.shell.time import Time
from ...tools import patterns, human

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import LimitBuilder, Result

Z3_BINARY = "z3"

Z3_STATIC: str = "-smt2 -st"

Z3_BUILDER: "LimitBuilder" = {
   "T": "-T:%s",
   "M": lambda giga: f"-memory:{int(1024*float(giga))}",
}

Z3_PAT: Pattern = re.compile(
   r"^.:([a-z-]*)\s*([0-9.]*)",
   flags=re.MULTILINE,
)

Z3_MEMOUT: Pattern = re.compile(
   r'error "out of memory"',
   flags=re.MULTILINE,
)


class Z3(StdinSolver):

   def __init__(
      self,
      limit: str,
      binary: str = Z3_BINARY,
      static: str = "",
      plugins: list["Plugin"] = [],
      complete: bool = True,
   ):
      cmd = f"{binary} {Z3_STATIC}"
      plugins = plugins + [
         Time(),
         Smt(complete=complete),
      ]
      StdinSolver.__init__(
         self,
         cmd,
         limit,
         Z3_BUILDER,
         plugins,
         1,
         static,
         True,
         True,
      )

   def process(self, output: str) -> "Result":
      result = patterns.keyval(Z3_PAT, output)
      result = patterns.mapval(result, human.numeric)
      if re.search(Z3_MEMOUT, output):
         result["status"] = "memout"
      return result

