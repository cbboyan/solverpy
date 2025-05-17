from typing import Any, TYPE_CHECKING
from .plugin import Plugin

if TYPE_CHECKING:
   from ..timedsolver import TimedSolver

class Translator(Plugin):

   def __init__(self, **kwargs):
      Plugin.__init__(self, **kwargs)

   def register(self, solver: "TimedSolver") -> None:
      solver.translators.append(self)

   def translate(self, instance: Any, strategy: Any) -> Any:
      return (instance, strategy)
