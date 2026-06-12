from typing import Pattern, TYPE_CHECKING
import re

from ..shellsolver import ShellSolver
from ..plugins.status.smt import Smt
from ..plugins.shell.time import Time
from ...tools import human, patterns

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import Result

LLM2SMT_BINARY = "llm2smt"

LLM2SMT_STATIC = "--quiet --stats"

LLM2SMT_STATS: Pattern = re.compile(
   r"^\s+([a-z][a-z0-9_.-]*?)\s*(-?[0-9]+(?:\.[0-9]+)?)\s*$",
   flags=re.MULTILINE,
)


class Llm2smt(ShellSolver):

   _binary = LLM2SMT_BINARY

   def __init__(
      self,
      limit: str,
      binary: str = LLM2SMT_BINARY,
      static: str = LLM2SMT_STATIC,
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
      result = patterns.keyval(LLM2SMT_STATS, output)
      return patterns.mapval(result, human.numeric)
