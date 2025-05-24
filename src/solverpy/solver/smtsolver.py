from typing import TYPE_CHECKING

from .shellsolver import ShellSolver
from .plugins.status.smt import Smt
from .plugins.shell.time import Time

if TYPE_CHECKING:
   from .plugins.plugin import Plugin
   from ..tools.typing import Builder, Result

SMT_OK = frozenset([
   'sat',
   'unsat',
])

SMT_FAILED = frozenset([
   'unknown',
])

SMT_TIMEOUT = frozenset([
   'timeout',
   'memout',
   'TIMEOUT',  # simulated timeout
])

SMT_ALL = SMT_OK | SMT_FAILED | SMT_TIMEOUT


class SmtSolver(ShellSolver):

   def __init__(
      self,
      cmd: str,
      limit: str,
      builder: "Builder" = {},
      plugins: list["Plugin"] = [],
      wait: (int | None) = None,
   ):
      plugins = plugins + [Time(), Smt()]
      ShellSolver.__init__(
         self,
         cmd,
         limit,
         builder,
         plugins,
         wait,
      )

   def valid(self, result: "Result") -> bool:
      return super().valid(result) and result["status"] in SMT_ALL

   @property
   def success(self) -> frozenset[str]:
      return SMT_OK

   @property
   def timeouts(self) -> frozenset[str]:
      return SMT_TIMEOUT

