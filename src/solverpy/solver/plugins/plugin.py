from typing import TYPE_CHECKING

from ..object import SolverPyObj
if TYPE_CHECKING:
   from ..timedsolver import TimedSolver

class Plugin(SolverPyObj):

   def __init__(self, **kwargs):
      SolverPyObj.__init__(self, **kwargs)

   def register(self, solver: "TimedSolver") -> None:
      raise NotImlementedError()

