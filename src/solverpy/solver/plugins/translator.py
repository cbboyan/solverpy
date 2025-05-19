from typing import Any, TYPE_CHECKING
from .plugin import Plugin

if TYPE_CHECKING:
   from ..solverpy import SolverPy

class Translator(Plugin):

   def __init__(self, **kwargs):
      Plugin.__init__(self, **kwargs)

   def register(self, solver: "SolverPy") -> None:
      solver.translators.append(self)

   def translate(
      self, 
      instance: Any, 
      strategy: Any
   ) -> tuple[Any, Any]:
      return (instance, strategy)
