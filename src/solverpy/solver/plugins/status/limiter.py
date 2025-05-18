from typing import TYPE_CHECKING, Any

from ..decorator import Decorator

if TYPE_CHECKING:
   from ...timedsolver import TimedSolver

class Limiter(Decorator):

   def __init__(self, **kwargs):
      Decorator.__init__(self, **kwargs)

   def register(self, solver : "TimedSolver") -> None: 
      super().register(solver)
      self.timeouts = solver.timeouts
      self.timeout = solver.limits.timeout
      self.limit = solver.limits.limit
   
   def update(
      self, 
      instance: Any, 
      strategy: Any, 
      output: Any, 
      result: dict
   ) -> None:
      if (not result) or ("status" not in result) or ("runtime" not in result):
         return
      if (result["status"] in self.timeouts) or \
            (result["runtime"] > self.timeout):
         result["runtime"] = self.timeout
      result["limit"] = self.limit
         

