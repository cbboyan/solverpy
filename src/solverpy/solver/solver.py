"""
# Abstract solver interface 

Defines a basic interface for all solvers.

## Implemented methods

+ The main method [solve][solverpy.solver.solver.Solver.solve] solves the
  problem and returns a processed result.  It calls `run` and `process` in
  sequence which need to implemented by subclasses.

+ Result queries 
  [valid][solverpy.solver.solver.Solver.valid],
  [solved][solverpy.solver.solver.Solver.solved] to recognize a valid and
  solved results.

## Abstract methods

+ running the solver: [run][solverpy.solver.solver.Solver.run]
+ processing the output: [process][solverpy.solver.solver.Solver.process]
+ status sets:
  [success][solverpy.solver.solver.Solver.success],
  [timeouts][solverpy.solver.solver.Solver.timeouts],
  [statuses][solverpy.solver.solver.Solver.statuses]
"""

from typing import Any, TYPE_CHECKING
from .object import SolverPyObj

if TYPE_CHECKING:
   from ..tools.typing import Result


class Solver(SolverPyObj):
   """
   Abstract class for solvers.
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

      Returns: the result
      """
      output = self.run(instance, strategy)
      self._output = output
      result = self.process(output)
      return result

   def valid(self, result: "Result") -> bool:
      """
      A valid status contains at least keys `status` and `runtime`. The status
      must be a valid status.

      Args:
          result: the result
      """
      return bool(result) and \
         ("status" in result) and \
         ("runtime" in result) and \
         (result["status"] in self.statuses)

   def solved(self, result: "Result") -> bool:
      """
      The result is solved if the status is in the success set.

      Args:
          result: the result
      """
      return bool(result) and \
         ("status" in result) and \
         (result["status"] in self.success)

   def run(self, instance: Any, strategy: Any) -> str:
      """
      Run the solver with the strategy on the instatnce.

      Args:
          instance: solver problem instance
          strategy: solver strategy

      Returns: raw solver output

      Raises:
          NotImplementedError: abstract method
      """
      del instance, strategy  # unused arguments
      raise NotImplementedError()

   def process(self, output: str) -> "Result":
      """
      Process the solver output and create the result.

      Args:
          output: raw solver output

      Returns: processed result dictionary
          

      Raises:
          NotImplementedError: abstract method
      """
      del output  # unused argument
      raise NotImplementedError()

   @property
   def name(self) -> str:
      """
      Solver name.  The default name is the class name.
      """
      return self.__class__.__name__

   @property
   def success(self) -> frozenset[str]:
      """
      The set of successful statuses.

      Raises:
          NotImplementedError: abstract property
      """
      raise NotImplementedError()
   
   @property
   def timeouts(self) -> frozenset[str]:
      """
      The set of timeout statuses.

      Raises:
          NotImplementedError: abstract property
      """
      raise NotImplementedError()
   
   @property
   def statuses(self) -> frozenset[str]:
      """
      The set of all valid statuses.

      Raises:
          NotImplementedError: abstract property
      """
      raise NotImplementedError()

