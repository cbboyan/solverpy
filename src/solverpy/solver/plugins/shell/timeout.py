from typing import Any, TYPE_CHECKING
from ..decorator import Decorator

if TYPE_CHECKING:
   from ...solverpy import SolverPy
   from ....tools.typing import Result

TIMEOUT_CMD = "timeout --kill-after=15 --foreground %s"


class Timeout(Decorator):

   def __init__(self, timeout: int):
      Decorator.__init__(self, timeout=timeout)
      self.timeout = timeout
      self.prefix = TIMEOUT_CMD % timeout

   def register(self, solver: "SolverPy") -> None:
      self.solver = solver
      solver.decorators.insert(0, self)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      del instance, strategy # unused arguments
      return f"{self.prefix} {cmd}"

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      del instance, strategy, output # unused arguments
      # see man(timeout) for timeout exit codes
      if self.solver._exitcode in [124, 137]:
         result["status"] = "TIMEOUT"

