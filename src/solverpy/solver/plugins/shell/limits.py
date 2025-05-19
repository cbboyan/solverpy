from typing import Any, TYPE_CHECKING

from ..plugin import Plugin
from ..decorator import Decorator
from ..translator import Translator

if TYPE_CHECKING:
   from ...solverpy import SolverPy
   from ....tools.typing import StrMaker, Builder


def build(fun: "StrMaker", arg: Any) -> str:
   return fun % arg if isinstance(fun, str) else fun(arg)


class Limits(Decorator, Translator):
   """
   This is either a decorator or a translator based on the value
   of `cmdline`.
   """

   def __init__(
      self,
      limit: str,
      builder: "Builder",
      cmdline: bool = True,
   ):
      Plugin.__init__(self, limit=limit, cmdline=cmdline)
      lims = {x[0]: x[1:] for x in limit.split("-") if x}
      assert "T" in lims
      self.timeout = int(lims["T"])
      self.memory = float(lims["M"]) if "M" in lims else None
      try:
         lims = [
            build(builder[x], y) for (x, y) in lims.items() if x in builder
         ]
      except Exception as e:
         print(e)
         raise Exception(f"solverpy: Invalid limit string: {limit}")

      delim = " " if cmdline else ""
      self.strat = delim.join(lims)
      self.cmdline = cmdline

      #self.args = " ".join(lims)
      self.limit = limit

   def register(self, solver: "SolverPy") -> None:
      if self.cmdline:
         solver.decorators.append(self)
      else:
         solver.translators.append(self)

   def __str__(self) -> str:
      return self.limit

   def __lt__(self, other):
      if self.limit and not other.limit:
         return None
      if self.memory and not other.memory:
         return None
      if not self.memory:
         return (self.timeout < other.timeout)
      else:
         return (self.timeout < other.timeout) or (self.memory < other.memory)

   #def __le__(self, other):
   #   return (self.key == other.key) or (self < other)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      del instance, strategy  # unused arguments
      if self.cmdline:
         return f"{cmd} {self.strategy}" if self.strategy else cmd
      else:
         return cmd

   def translate(
      self,
      instance: Any,
      strategy: str,
   ) -> tuple[Any, str]:
      if not self.cmdline:
         return (instance, self.strategy + strategy)
      else:
         return (instance, strategy)

   @property
   def strategy(self) -> str:
      return self.strat

