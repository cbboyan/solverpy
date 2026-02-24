from typing import Any

from ..object import SolverPyObj

class Plugin(SolverPyObj):
   """Base class for plugins."""

   def __init__(self, pid: str | None = None, **kwargs: Any):
      SolverPyObj.__init__(self, **kwargs)
      self._enabled = True
      self._id = pid

   def register(self, solver: Any) -> None:
      del solver # unused argument
      raise NotImplementedError()
   
   def enable(self):
      self._enabled = True

   def disable(self):
      self._enabled = False

   @property
   def id(self) -> str | None:
      return self._id


