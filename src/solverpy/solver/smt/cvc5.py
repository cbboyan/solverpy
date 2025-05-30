from typing import Any, TYPE_CHECKING
import re

from ..shellsolver import ShellSolver
from ..plugins.status.smt import Smt
from ..plugins.shell.time import Time
from ...tools import patterns, human

if TYPE_CHECKING:
   from typing import Pattern
   from ..plugins.plugin import Plugin
   from ...tools.typing import LimitBuilder, Result

CVC5_BINARY = "cvc5"

CVC5_STATIC: str = "-Lsmt2 --stats --stats-internal"

CVC5_BUILDER: "LimitBuilder" = {
   "T": lambda x: "--tlimit=%s" % (1000 * int(x)),
   "R": lambda x: "--rlimit=%s" % x
}

CVC5_KEYS = [
   "driver::totalTime",
   "global::totalTime",
   "resource::resourceUnitsUsed",
   "resource::steps::resource",
   "Instantiate::[^ ]*",
   "QuantifiersEngine::[^ ]*",
   "SharedTermsDatabase::termsCount",
   "sat::conflicts",
   "sat::decisions",
   "sat::clauses_literals",
   "sat::propagations",
]

# TODO: extend with:
#   GNU MP: Cannot allocate memory
#   (error "std::bad_alloc")
#   terminate called after throwing an instance of 'std::bad_alloc'
#   [LightGBM] [Warning] std::bad_alloc

CVC5_TIMEOUT = re.compile(r"cvc5 interrupted by (timeout)")


class Cvc5(ShellSolver):

   def __init__(
      self,
      limit: str,
      binary: str = CVC5_BINARY,
      static: str = CVC5_STATIC,
      plugins: list["Plugin"] = [],
      keys: list[str] = CVC5_KEYS,
      complete: bool = True,
   ):
      cmd = f"{binary} {static}"
      plugins = plugins + [
         Time(),
         Smt(complete=complete),
      ]
      ShellSolver.__init__(
         self,
         cmd,
         limit,
         CVC5_BUILDER,
         plugins,
         wait=1,
      )
      self.pattern: "Pattern" = re.compile(
         r"^(%s) = (.*)$" % "|".join(keys),
         flags=re.MULTILINE,
      )

   def process(self, output: str) -> "Result":

      def parseval(val: str) -> Any:  # value or dict of values
         if val.startswith("{") and val.endswith("}"):
            val0 = val.strip(" {}")
            val0 = val0.split(",")
            val0 = [x.split(":") for x in val0]
            return {x.strip(): human.numeric(y.strip()) for (x, y) in val0}
         return human.numeric(val)

      result = patterns.keyval(self.pattern, output)
      result = patterns.mapval(result, parseval)
      timeouted = patterns.single(CVC5_TIMEOUT, output, "")
      if timeouted:
         result["status"] = timeouted  # timeouted == "timeout"
      return result
