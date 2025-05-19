from typing import Pattern, TYPE_CHECKING
import re

from ..tptpsolver import TptpSolver
from ..smt.cvc5 import CVC5_BINARY, CVC5_STATIC, CVC5_KEYS, CVC5_BUILDER
from ..smt.cvc5 import Cvc5 as SmtCvc5

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import Result


class Cvc5(TptpSolver):

   def __init__(
      self,
      limit: str,
      binary: str = CVC5_BINARY,
      static: str = CVC5_STATIC,
      plugins: list["Plugin"] = [],
      keys: list[str] = CVC5_KEYS,
   ):
      cmd = f"{binary} --lang=tptp {static}"
      TptpSolver.__init__(self, cmd, limit, CVC5_BUILDER, plugins, wait=1)
      self.pattern: Pattern = re.compile(
         r"^(%s) = (.*)$" % "|".join(keys),
         flags=re.MULTILINE,
      )

   def process(self, output: str) -> "Result":
      result = SmtCvc5.process(self, output)  # type: ignore
      if ("status" in result) and (result["status"] == "timeout"):
         result["status"] = "Timeout"
      return result

