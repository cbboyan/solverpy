from typing import Any, Pattern, TYPE_CHECKING
import re
import logging

from ..stdinsolver import StdinSolver
from ..plugins.status.smt import Smt
from ..plugins.shell.time import Time
from ...tools import patterns, human

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import LimitBuilder, Result

logger = logging.getLogger(__name__)

Z3_BINARY = "z3"

Z3_STATIC: str = "-smt2 -st"

Z3_BUILDER: "LimitBuilder" = {
   "T": "-T:%s",
   "M": lambda giga: f"-memory:{int(1024*float(giga))}",
   "R": "rlimit=%s",
}

Z3_PAT: Pattern = re.compile(
   r"^.:([a-z-]*)\s*([0-9.]*)",
   flags=re.MULTILINE,
)

Z3_MEMOUT: Pattern = re.compile(
   r'error "out of memory"',
   flags=re.MULTILINE,
)

Z3_CHECKSAT = re.compile(
   r"\(check-sat.*$",
   flags=re.MULTILINE,
)

Z3_USING = re.compile(
   r"^;(\(check-sat-using .*)$",
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

   def input(self, instance: Any, strategy: Any) -> bytes:
      (instance, strategy) = self.translate(instance, strategy)
      inputstr = self._static.encode()
      inputstr += strategy.encode()
      inputstr += b"\n"
      mo = Z3_USING.search(strategy)
      if mo:
         check = mo.group(1)
         in0 = open(instance, "r").read()
         (in0, count) = Z3_CHECKSAT.subn(check, in0)
         if count != 1:
            logger.warning(f"Unexpected number ({count}) of 'check-sat' patterns in instance '{instance}' for strategy '{strategy}'.")
         inputstr += in0.encode()
      else:
         inputstr += open(instance, "rb").read()
      #open(f"/tmp/solverpy-tmp.smt2", "wb").write(inputstr)
      return inputstr
