from typing import Any, TYPE_CHECKING

from ..plugin import Plugin
from ..decorator import Decorator
from ..translator import Translator

if TYPE_CHECKING:
   from ...solverpy import SolverPy
   from ....tools.typing import StrMaker, LimitBuilder


def build(fun: "StrMaker", arg: Any) -> str:
   return fun % arg if isinstance(fun, str) else fun(arg)


class Limits(Decorator, Translator):
   """Parse a resource-limit string and apply solver-specific CLI flags.

   `Limits` can operate as either a
   [`Decorator`][solverpy.solver.plugins.decorator.Decorator] or a
   [`Translator`][solverpy.solver.plugins.translator.Translator] depending on
   the `cmdline` flag:

   - `cmdline=True` *(default)* — registers as a decorator; `decorate()` appends
     the constructed flags to the shell command (e.g. `--cpu-limit=10`).
   - `cmdline=False` — registers as a translator; `translate()` prepends the
     flags to the strategy string so the solver receives them as part of its
     options input.

   The limit string uses the format `T<seconds>[-M<gigabytes>]`, e.g.:

   - `"T10"` — 10-second CPU/wall-clock limit
   - `"T10-M4"` — 10 seconds and 4 GB memory limit

   Each flag letter is mapped to a CLI template via the `builder` dict provided
   by the concrete solver subclass.
   """

   def __init__(
      self,
      limit: str,
      builder: "LimitBuilder",
      cmdline: bool = True,
      inputfile: bool = False,
   ):
      Plugin.__init__(
         self,
         limit=limit,
         cmdline=cmdline,
      )
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
      self._inputfile = inputfile

   def register(self, solver: "SolverPy") -> None:
      """Register as a decorator or translator depending on `cmdline`."""
      if self.cmdline:
         solver.decorators.append(self)
      else:
         solver.translators.append(self)

   def __str__(self) -> str:
      return self.limit

   def __lt__(self, other: "Limits") -> bool | None:
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
      """Append limit flags to *cmd* when `cmdline=True` (no-op otherwise).

      An optional `/dev/stdin` suffix is appended when `inputfile=True` so that
      solvers that read the problem from stdin receive the correct filename.
      """
      del instance, strategy  # unused arguments
      if self.cmdline:
         input = " /dev/stdin" if self._inputfile else ""
         return f"{cmd} {self.strategy}{input}" if self.strategy else cmd
      else:
         return cmd

   def translate(
      self,
      instance: Any,
      strategy: str,
   ) -> tuple[Any, str]:
      """Prepend limit flags to *strategy* when `cmdline=False` (no-op otherwise)."""
      if not self.cmdline:
         return (instance, self.strategy + strategy)
      else:
         return (instance, strategy)

   @property
   def strategy(self) -> str:
      """The constructed CLI flag string derived from the limit string."""
      return self.strat
