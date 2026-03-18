from typing import Any, TYPE_CHECKING
from .plugin import Plugin

if TYPE_CHECKING:
   from ..solverpy import SolverPy
   from ...tools.typing import Result


class Decorator(Plugin):
   """Plugin that wraps the solver command and post-processes the result.

   Decorators are applied in registration order by
   [`PluginSolver`][solverpy.solver.pluginsolver.PluginSolver] at three points
   in the solve lifecycle:

   1. `decorate()` — called before the subprocess launches; each decorator may
      wrap or extend the command string.
   2. `update()` — called after the subprocess exits; reads raw output and
      populates the `result` dict.
   3. `finished()` — called after all `update()` calls complete; used for
      side-effects (e.g. writing output files) that depend on the final result
      state.

   All three methods are no-ops by default; subclasses override only what they
   need.
   """

   def __init__(self, **kwargs):
      Plugin.__init__(self, **kwargs)

   def register(self, solver: "SolverPy") -> None:
      """Append this decorator to `solver.decorators`."""
      solver.decorators.append(self)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      """Wrap or extend the shell command before the subprocess launches.

      Args:
         cmd: The command string built so far.
         instance: The (translated) problem instance.
         strategy: The (translated) strategy string.

      Returns:
         The modified command string.  The default implementation returns
         *cmd* unchanged.
      """
      del instance, strategy  # unused arguments
      return cmd

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      """Extract data from *output* and update *result* in place.

      Called after the subprocess exits, in decorator registration order.

      Args:
         instance: The problem instance that was solved.
         strategy: The strategy that was used.
         output: Combined stdout (and stderr, if captured) from the subprocess.
         result: The result dict being constructed; modify it in place.
      """
      del instance, strategy, output, result  # unused arguments
      return

   def finished(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      """Perform side-effects after all `update()` calls have completed.

      Called once the result dict is fully populated.  Useful for writing
      files or logging that depends on the final status (e.g.
      [`Outputs`][solverpy.solver.plugins.db.outputs.Outputs]).

      Args:
         instance: The problem instance that was solved.
         strategy: The strategy that was used.
         output: Raw subprocess output.
         result: The completed result dict.
      """
      del instance, strategy, output, result  # unused arguments
      return

