from typing import Any

from ..object import SolverPyObj

class Plugin(SolverPyObj):
   """Base class for plugins."""

   def __init__(self, pid: str | None = None, **kwargs: Any):
      SolverPyObj.__init__(self, **kwargs)
      self._id = pid

   def register(self, solver: Any) -> None:
      del solver # unused argument
      raise NotImplementedError()

   @property
   def id(self) -> str | None:
      return self._id


