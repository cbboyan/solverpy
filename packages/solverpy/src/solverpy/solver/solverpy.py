"""
# Resource limits and result caching

`SolverPy` extends [`PluginSolver`][solverpy.solver.pluginsolver.PluginSolver]
with two concerns:

* **Resource limits** — a [`Limits`][solverpy.solver.plugins.shell.limits.Limits]
  object (time/memory) is created at construction and a
  [`Limiter`][solverpy.solver.plugins.status.limiter.Limiter] decorator is
  automatically registered to translate exit codes into timeout statuses.
* **Result simulation** — [`simulate`][solverpy.solver.solverpy.SolverPy.simulate]
  checks whether a cached result from a previous run is still applicable under
  the current resource limits, avoiding redundant solver invocations.
"""

from typing import Any, TYPE_CHECKING

from .pluginsolver import PluginSolver
from .plugins.shell.limits import Limits
from .plugins.status.limiter import Limiter

if TYPE_CHECKING:
   from .plugins.plugin import Plugin
   from ..tools.typing import Result


class SolverPy(PluginSolver):
   """
   Extends `PluginSolver` with resource limits and cached-result simulation.

   Concrete solver subclasses (e.g. `ShellSolver`, `StdinSolver`) build on
   this class and supply the actual solver binary invocation.
   """

   def __init__(
      self,
      limits: Limits,
      plugins: list["Plugin"] = [],
      **kwargs: Any,
   ):
      """
      Args:
          limits: resource limits (time/memory) for solver runs.
          plugins: additional plugins to register (a `Limiter` is always appended).
          **kwargs: forwarded to `PluginSolver.__init__`.
      """
      assert limits.limit.startswith("T")
      self._limits: Limits = limits
      self._exitcode: int = -1
      self._timeouts = frozenset()
      self._success = frozenset()
      self._statuses = frozenset()
      plugins = plugins + [
         Limiter(),
      ]
      PluginSolver.__init__(self, plugins=plugins, **kwargs)

   def __hash__(self) -> int:
      """Hash based on the solver's string representation."""
      return hash(str(self))

   def __eq__(self, other: object) -> bool:
      """Two solvers are equal when their string representations match."""
      if not isinstance(other, SolverPy):
         return False
      return str(self) == str(other)

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
      elif result["status"] in self.statuses:
         # the cached result is unknow/GaveUp
         oldlimits = Limits(result["limit"], {})
         if oldlimits > self._limits:
            # recompute if we have less resources (maybe timeout?)
            # TODO: is this correct?
            return None
      else:
         # recompute unknown results (GaveUp, unknown)
         # TODO: do we want to always recompute?
         return None
      # the result is applicable without changes
      return result

   @property
   def timeouts(self) -> frozenset[str]:
      """The set of timeout statuses, populated by the solver's status plugin."""
      return self._timeouts

   @property
   def success(self) -> frozenset[str]:
      """The set of successful statuses, populated by the solver's status plugin."""
      return self._success

   @property
   def statuses(self) -> frozenset[str]:
      """The set of all valid statuses, populated by the solver's status plugin."""
      return self._statuses


