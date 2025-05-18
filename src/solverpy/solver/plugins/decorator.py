from typing import Any, TYPE_CHECKING
from .plugin import Plugin

if TYPE_CHECKING:
   from ..timedsolver import TimedSolver

class Decorator(Plugin):

   def __init__(self, **kwargs):
      Plugin.__init__(self, **kwargs)

   def register(self, solver: "TimedSolver") -> None:
      solver.decorators.append(self)
   
   def decorate(
      self, 
      cmd: str, 
      instance: Any, 
      strategy: Any
   ) -> str:
      return cmd

   def update(
      self, 
      instance: Any, 
      strategy: Any, 
      output: str, 
      result: dict
   ) -> None:
      return 

   def finished(
      self, 
      instance: Any, 
      strategy: Any,
      output: str,
      result: dict
   ) -> None:
      return

