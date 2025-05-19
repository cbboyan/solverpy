from typing import TYPE_CHECKING

from ..object import SolverPyObj
if TYPE_CHECKING:
   from ..pluginsolver import PluginSolver

class Plugin(SolverPyObj):

   def __init__(self, **kwargs):
      SolverPyObj.__init__(self, **kwargs)

   def register(self, solver: "PluginSolver") -> None:
      del solver
      raise NotImplementedError()

