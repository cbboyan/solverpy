from typing import TYPE_CHECKING

from .shellsolver import ShellSolver
from .plugins.status.tptp import Tptp
from .plugins.shell.time import Time

if TYPE_CHECKING:
   from .plugins.plugin import Plugin
   from ..tools.typing import Builder, Result

TPTP_OK = frozenset([
   'Satisfiable',
   'Unsatisfiable',
   'Theorem',
   'CounterSatisfiable',
   'ContradictoryAxioms',
])

TPTP_FAILED = frozenset([
   'GaveUp',
])

TPTP_TIMEOUT = frozenset([
   'ResourceOut',
   'Timeout',
   "TIMEOUT",  # simulated timeout
])

TPTP_INCOMPLETE = frozenset([
   'Satisfiable',
   'CounterSatisfiable',
])

TPTP_ALL = TPTP_OK | TPTP_FAILED | TPTP_TIMEOUT

INC_OK = TPTP_OK - TPTP_INCOMPLETE


class TptpSolver(ShellSolver):

   def __init__(
      self,
      cmd: str,
      limit: str,
      builder: "Builder" = {},
      plugins: list["Plugin"] = [],
      wait: (int | None) = None,
      complete: bool = True,
   ):
      plugins = plugins + [Time(), Tptp()]
      ShellSolver.__init__(
         self,
         cmd,
         limit,
         builder,
         plugins,
         wait,
      )
      self.complete = complete

   def valid(self, result: "Result") -> bool:
      return super().valid(result) and result["status"] in TPTP_ALL

   @property
   def success(self) -> frozenset[str]:
      return TPTP_OK if self.complete else INC_OK

   @property
   def timeouts(self) -> frozenset[str]:
      return TPTP_TIMEOUT
