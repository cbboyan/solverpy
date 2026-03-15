from typing import Any, TYPE_CHECKING
from .plugin import Plugin

if TYPE_CHECKING:
   from ..solverpy import SolverPy
   from ...tools.typing import Result


class Decorator(Plugin):

   def __init__(self, **kwargs):
      Plugin.__init__(self, **kwargs)

   def register(self, solver: "SolverPy") -> None:
      solver.decorators.append(self)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      del instance, strategy  # unused arguments
      return cmd

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      del instance, strategy, output, result  # unused arguments
      return

   def finished(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      del instance, strategy, output, result  # unused arguments
      return

