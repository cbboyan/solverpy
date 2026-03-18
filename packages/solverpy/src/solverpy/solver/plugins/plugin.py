from typing import Any

from ..object import SolverPyObj

class Plugin(SolverPyObj):
   """Base class for all solver plugins.

   A plugin is attached to a
   [`PluginSolver`][solverpy.solver.pluginsolver.PluginSolver] at construction
   time via the `plugins` list.  When `init()` is called, each plugin's
   `register()` method fires, giving the plugin a reference to the solver and
   placing it on either `solver.decorators` or `solver.translators`.

   Plugins can be toggled at runtime via `enable()` / `disable()`.  To target a
   specific plugin from outside the solver, assign a string `pid` at construction
   and call `solver.call(pid, method)`.
   """

   def __init__(self, pid: str | None = None, **kwargs: Any):
      """Initialise the plugin.

      Args:
         pid: Optional string identifier used by
            [`PluginSolver.call`][solverpy.solver.pluginsolver.PluginSolver.call]
            to dispatch method calls to this plugin.
         **kwargs: Forwarded to `SolverPyObj` for repr support.
      """
      SolverPyObj.__init__(self, **kwargs)
      self._enabled = True
      self._id = pid

   def register(self, solver: Any) -> None:
      """Register this plugin with *solver*.

      Called once by
      [`PluginSolver.init`][solverpy.solver.pluginsolver.PluginSolver.init].
      Subclasses append themselves to `solver.decorators` or
      `solver.translators` (or both, in the case of
      [`Limits`][solverpy.solver.plugins.shell.limits.Limits]).

      Raises:
         NotImplementedError: Must be overridden by every concrete subclass.
      """
      del solver # unused argument
      raise NotImplementedError()

   def enable(self) -> None:
      """Re-enable this plugin after a previous `disable()` call."""
      self._enabled = True

   def disable(self) -> None:
      """Disable this plugin so its hooks become no-ops until re-enabled."""
      self._enabled = False

   @property
   def id(self) -> str | None:
      """The optional string identifier assigned at construction time."""
      return self._id


