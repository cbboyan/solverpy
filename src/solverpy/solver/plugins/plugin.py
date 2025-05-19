from typing import TYPE_CHECKING

from ..object import SolverPyObj
if TYPE_CHECKING:
   from ..solverpy import SolverPy

class Plugin(SolverPyObj):

   def __init__(self, **kwargs):
      SolverPyObj.__init__(self, **kwargs)

   def register(self, solver: "SolverPy") -> None:
      del solver # unused argument
      raise NotImplementedError()

