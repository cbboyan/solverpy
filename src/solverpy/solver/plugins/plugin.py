from typing import Any

from ..object import SolverPyObj

class Plugin(SolverPyObj):

   def __init__(self, **kwargs: Any):
      SolverPyObj.__init__(self, **kwargs)

   def register(self, solver: Any) -> None:
      del solver # unused argument
      raise NotImplementedError()

