"""
# Abstract solver interface 

The class [`Solver`][solverpy.solver.solver.Solver] encapsulates the very basic
solver functionality --- solving a single problem instance and processing the
output. The class defines solver-specific set of statuses, which are typically
strings representing TPTP statuses (like `Theorem`, `Unsatisfiable`, etc), or
SMT statuses (like `sat`, `unsat`, etc). The main method
[`solve`][solverpy.solver.solver.Solver.solve] runs the solver and returns a
processed result. The result is the SolverPy
[`Result`][solverpy.solver.solver.Result] dictionary containing at least keys
`status` and `runtime`. Although the result can contain solver-specific keys,
the basic result structure is shared between all solvers. This makes the result
comparable between solvers.
The plugin functionality is added in the superclass class
[`PluginSolver`][solverpy.solver.pluginsolver.PluginSolver].
"""

from typing import Any, TYPE_CHECKING
from .object import SolverPyObj

if TYPE_CHECKING:
   from ..tools.typing import Result


class Solver(SolverPyObj):
   """
   Base abstract class for all solvers encapsulating the very basic solver
   functionality. The implementing class must provide the set of statuses, and
   implement methods [`run`][solverpy.solver.solver.Solver.run] and
   [`process`][solverpy.solver.solver.Solver.process] which run the solver on a
   single problem instance and process the solver output.

   ```plantuml name="solver-solver"
   abstract class solverpy.solver.solver.Solver extends solverpy.solver.object.SolverPyObj {
      {abstract} # success : frozenset[Status]
      {abstract} # timeouts : frozenset[Status]
      {abstract} # statuses : frozenset[Status]
      {abstract} # run(instance, strategy) : str
      {abstract} # process(output) : Result
      + solve(instance, strategy) : Result
      + valid(result) : bool
      + solved(result) : bool
   }
   abstract class solverpy.solver.pluginsolver.PluginSolver extends solverpy.solver.solver.Solver 
   ```
   
   The main method is [`solve`][solverpy.solver.solver.Solver.solve] which
   calls the solver on a problem instance and returns a processed result --- by
   default it calls `run` and `process` in sequence. Result query methods
   [valid][solverpy.solver.solver.Solver.valid] and
   [solved][solverpy.solver.solver.Solver.solved] are implemented to recognize
   a valid and successfully solved results.

   The values of `instance` and `strategy` in `solve` are completely
   solver-specific at this level. The [`Result`][solverpy.tools.typing.Result]
   is, however, always a dictionary guaranteed to contain at least the keys
   `status` and `runtime`. The value of `status` is one of
   [`statuses`][solverpy.solver.solver.Solver.statuses] and the value of
   `runtime` is the solver runtime in seconds.

   The statuses are also solver-specific. The set
   [`success`][solverpy.solver.solver.Solver.success] contains all successful
   statuses, and similarly [`timeouts`][solverpy.solver.solver.Solver.timeouts]
   contains timeouting statuses. Both sets
   [`timeouts`][solverpy.solver.solver.Solver.timeouts] and
   [`success`][solverpy.solver.solver.Solver.success] are expected to be
   subsets of [`statuses`][solverpy.solver.solver.Solver.statuses] which
   contain all valid statuses.
   """

   def __init__(self, **kwargs: Any):
      SolverPyObj.__init__(self, **kwargs)

   def __str__(self) -> str:
      return self.name

   def solve(self, instance: Any, strategy: Any) -> "Result":
      """
      Run the solver with the strategy on the instatance. Process the output
      and create the result.

      Args:
          instance: solver problem instance (filename, or a bid-problem
              pair, or custom). 
          strategy: solver strategy (filename, sid, or custom).

      Returns: 
          The SolverPy result dictionary.
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

      Returns: 
          raw solver output
      """
      del instance, strategy  # unused arguments
      raise NotImplementedError()

   def process(self, output: Any) -> "Result":
      """
      Process the solver output and create the result.

      Args:
          output: raw solver output

      Returns: 
          processed result dictionary
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
      """
      raise NotImplementedError()
   
   @property
   def timeouts(self) -> frozenset[str]:
      """
      The set of timeout statuses.
      """
      raise NotImplementedError()
   
   @property
   def statuses(self) -> frozenset[str]:
      """
      The set of all valid statuses.
      """
      raise NotImplementedError()

