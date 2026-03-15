from typing import TYPE_CHECKING, Any

from ..decorator import Decorator

if TYPE_CHECKING:
   from ...solverpy import SolverPy
   from ....tools.typing import Result


class Limiter(Decorator):

   def __init__(self, **kwargs):
      Decorator.__init__(self, **kwargs)

   def register(self, solver: "SolverPy") -> None:
      super().register(solver)
      self.timeouts = solver.timeouts
      self.timeout = solver._limits.timeout
      self.limit = solver._limits.limit

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: Any,
      result: "Result",
   ) -> None:
      del instance, strategy, output # unused arguments
      if (not result) or ("status" not in result) or ("runtime" not in result):
         return
      if (result["status"] in self.timeouts) or \
            (result["runtime"] > self.timeout):
         result["runtime"] = self.timeout
      result["limit"] = self.limit

