"""
Abstract solver module.

Tada!

"""

from typing import Any, TYPE_CHECKING
from .object import SolverPyObj

if TYPE_CHECKING:
   from ..tools.typing import Result


class Solver(SolverPyObj):
   """
   Class Solver.

   jada!
   """

   def __init__(self, **kwargs: Any):
      SolverPyObj.__init__(self, **kwargs)

   def __str__(self) -> str:
      return self.name

   def solve(self, instance: Any, strategy: Any) -> Any:
      """
      Run the solver with the strategy on the instatance. Process the output
      and create the result.

      Args:
          instance: solver problem instance (filename, or a bid-problem
              pair, or custom). 
          strategy: solver strategy (filename, sid, or custom).

      Returns: output and result
      """
      output = self.run(instance, strategy)
      result = self.process(output)
      return (output, result)

   def valid(self, result: "Result") -> bool:
      """Is the result valid?"""
      return bool(result) and ("status" in result) and ("runtime" in result)

   def solved(self, result: "Result") -> bool:
      """Is the result solved?"""
      return bool(result) and ("status" in result) and \
         (result["status"] in self.success)

   def run(self, instance: Any, strategy: Any) -> str:
      """Run the solver with the strategy on the instatance. Return the output."""
      del instance, strategy  # unused arguments
      raise NotImplementedError()

   def process(self, output: str) -> "Result":
      """Process the solver output and create the result."""
      del output  # unused argument
      raise NotImplementedError()

   @property
   def name(self) -> str:
      """Solver name."""
      return self.__class__.__name__

   @property
   def success(self) -> frozenset[str]:
      """The set of successful statuses."""
      raise NotImplementedError()
