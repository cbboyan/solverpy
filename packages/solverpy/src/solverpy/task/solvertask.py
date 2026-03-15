"""
Defines the [`SolverTask`][solverpy.task.solvertask.SolverTask] class.
"""

from typing import TYPE_CHECKING, Any
from .task import Task
from .talker import Talker

if TYPE_CHECKING:
   from ..solver.solverpy import SolverPy
   from ..tools.typing import Result


class SolverTask(Task):
   """
   Represents a task to be executed by a
   [`SolverPy`][solverpy.solver.solverpy.SolverPy] solver. 
   This is a basic interface for the database which stores results
   of [`SolverTask`][solverpy.task.solvertask.SolverTask].
   """

   def __init__(
      self,
      solver: "SolverPy",
      bid: str,
      sid: str,
      problem: str,
      calls: list[tuple[str, str, Any, Any]] = [],
   ):
      """
      Create a new task to execute `solver` on problem `problem` from benchmark
      `bid` using strategy `sid`.

      Args:
          solver: the solver based on [`SolverPy`][solverpy.solver.solverpy.SolverPy]
          bid: the benchmark id
          sid: the strategy id
          problem: the problem from the benchmark
          calls: the plugin calls to be executed before solving the task
      """
      Task.__init__(self)
      self._solver = solver
      self.bid = bid
      self.sid = sid
      self.problem = problem
      self._calls = calls

   def __str__(self) -> str:
      return f"{self.solver}:{self.sid} @ {self.bid} / {self.problem}"

   def __eq__(self, other):
      if not isinstance(other, self.__class__):
         return False
      return (f"{self.solver}" == f"{other.solver}" \
         and self.bid == other.bid \
         and self.sid == other.sid \
         and self.problem == other.problem)

   def __hash__(self):
      return hash((
         str(self.solver),
         self.bid,
         self.sid,
         self.problem,
      ))

   def run(self) -> "Result":
      """
      Run the task and return the result. 

      First, plugin calls from `calls` given to the constructor are executed on
      the [`solver`][solverpy.task.solvertask.SolverTask.solver]. Then,
      [`SolverPy.solve`][solverpy.solver.solverpy.SolverPy.solve] is called on
      [`instance`][solverpy.task.solvertask.SolverTask.instance] and
      [`strategy`][solverpy.task.solvertask.SolverTask.strategy].

      Returns: 
         the result dictionary
      """
      if self.logqueue:
         Talker.log_config(self.logqueue)
      for (pid, method, args, kwargs) in self._calls:
         self.solver.call(pid, method, *args, **kwargs)
      return self.solver.solve(self.instance, self.strategy)

   def status(self, result: "Result") -> bool | None:
      """
      Translate the result to (typically smaller) status to send it over the
      queue.

      Args:
          result: the result

      Returns:
          the status
      """
      if not self.solver.valid(result):
         return None
      return self.solver.solved(result)

   @property
   def instance(self) -> tuple[str, str]:
      """
      Get the instance of this solver task as a benchmark-problem pair.

      Returns:
          the pair of benchmark id and problem name
      """
      return (self.bid, self.problem)

   @property
   def strategy(self) -> str:
      """
      Get the strategy of this solver task as a strategy id.

      Returns:
          the strategy
      """
      return self.sid

   @property
   def solver(self) -> "SolverPy":
      """
      Get the [`SolverPy`][solverpy.solver.solverpy.SolverPy] solver of this solver task.

      Returns:
          the solver
      """
      return self._solver
