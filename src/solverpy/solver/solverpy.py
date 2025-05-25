from typing import TYPE_CHECKING

from .pluginsolver import PluginSolver
from .plugins.shell.limits import Limits
from .plugins.status.limiter import Limiter

if TYPE_CHECKING:
   from .plugins.plugin import Plugin
   from ..tools.typing import Result


class SolverPy(PluginSolver):

   def __init__(
      self,
      limits: Limits,
      plugins: list["Plugin"] = [],
   ):
      assert limits.limit.startswith("T")
      self._limits: Limits = limits
      self._exitcode: int = -1
      new = [Limiter()]
      PluginSolver.__init__(self, plugins=plugins + new)

   @property
   def timeouts(self) -> frozenset[str]:
      "The set of timeout statuses."
      raise NotImplementedError()

   #def determine(self, result) # TODO: rename
   def simulate(self, result: "Result") -> "Result | None":
      "Simulate run from the past result."
      if result["status"] in self.timeouts:
         #if result["status"] not in self.success: # we might want this?
         oldlimits = Limits(result["limit"], {})
         # the cached result is timeout
         if oldlimits < self._limits:
            #if result["runtime"] < self.timeout:
            # recompute since we have more time or/and space
            return None
      elif result["status"] in self.success:
         # the cached result is solved
         if result["runtime"] > self._limits.timeout:
            #if result["runtime"] > self.timeout:
            # simulated timeout
            return dict(
               result,
               status="TIMEOUT",
               runtime=self._limits.timeout,
            )
      else:
         # recompute unknown results (GaveUp, unknown)
         # TODO: do we want to always recompute?
         return None
      # the result is applicable without changes
      return result

   #def simulate(self, result):
   #   "Simulate run from the past result."
   #   if result["status"] in self.timeouts:
   #      # the cached result is timeout
   #         # recompute since we have more time
   #         return None
   #   else:
   #      # the cached result is solved
   #         # simulated timeout
   #         return dict(result,
   #                     status="TIMEOUT",
   #                     runtime=self.timeout)
   #   # the result is applicable without changes
   #   return result
