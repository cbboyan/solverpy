from typing import TYPE_CHECKING
from .task import Task

if TYPE_CHECKING:
   from ..solver.solverpy import SolverPy
   from ..tools.typing import Result


class SolverTask(Task):

   def __init__(
      self,
      solver: "SolverPy",
      bid: str,
      sid: str,
      problem: str,
   ):
      Task.__init__(self)
      self.solver = solver
      self.bid = bid
      self.sid = sid
      self.problem = problem

   def __str__(self) -> str:
      return f"{self.solver}:{self.sid} @ {self.bid} / {self.problem}"

   def run(self) -> "Result":
      return self.solver.solve(self.instance, self.strategy)

   def status(self, result: "Result") -> bool | None:
      if not self.solver.valid(result):
         return None
      return self.solver.solved(result)

   @property
   def instance(self) -> tuple[str, str]:
      return (self.bid, self.problem)

   @property
   def strategy(self) -> str:
      return self.sid

