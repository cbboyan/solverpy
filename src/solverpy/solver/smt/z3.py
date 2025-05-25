from typing import Pattern, TYPE_CHECKING
import re

from ..stdinsolver import StdinSolver
from ..smtsolver import SMT_ALL, SMT_OK, SMT_TIMEOUT
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


class Z3(StdinSolver):

   def __init__(
      self,
      limit: str,
      binary: str = Z3_BINARY,
      static: str = "",
      plugins: list["Plugin"] = [],
   ):
      cmd = f"{binary} {Z3_STATIC}"
      plugins = plugins + [Time(), Smt()]
      StdinSolver.__init__(
         self,
         cmd,
         limit,
         Z3_BUILDER,
         plugins,
         1,
         static,
         True,
         True
      )

   def process(self, output: str) -> "Result":
      result = patterns.keyval(Z3_PAT, output)
      result = patterns.mapval(result, human.numeric)
      if re.search(Z3_MEMOUT, output):
         result["status"] = "memout"
      return result
   
   def valid(self, result: "Result") -> bool:
      return super().valid(result) and result["status"] in SMT_ALL

   @property
   def success(self) -> frozenset[str]:
      return SMT_OK

   @property
   def timeouts(self) -> frozenset[str]:
      return SMT_TIMEOUT

