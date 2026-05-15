"""
# Reloader — replay solver runs from cached outputs

`Reloader` wraps an existing `SolverPy` solver and replays previously
recorded runs by reading the raw output from the `outputs/` cache directory
instead of re-invoking the binary.  All plugin calls (`decorate`, `update`,
`translate`) are delegated to the wrapped solver so that result processing
is identical to a live run.

Typical use: re-process cached outputs with updated parsing logic without
re-running the (expensive) solver.
"""

from typing import Any, TYPE_CHECKING
import logging

from .solverpy import SolverPy
from .plugins.db.outputs import Outputs

if TYPE_CHECKING:
   from .plugins.plugin import Plugin
   from ..tools.typing import Result

logger = logging.getLogger(__name__)


class Reloader(SolverPy):
   """
   A `SolverPy` that replays runs from cached output files instead of
   invoking the solver binary.  Delegates all processing to the wrapped solver.
   """

   def __init__(
      self,
      solver: SolverPy,
      plugins: list["Plugin"] = [],
      flatten: bool = True,
      compress: bool = True,
   ):
      """
      Args:
          solver: the wrapped solver whose output cache and processing logic to reuse.
          plugins: additional plugins registered on this reloader instance.
          flatten: passed to `Outputs` — replace `/` in problem paths with `_._`.
          compress: passed to `Outputs` — read `.gz` files.
      """
      self.solver = solver
      SolverPy.__init__(
         self,
         solver._limits,
         plugins,
      )
      self.outputs = Outputs(flatten=flatten, compress=compress)
      self.outputs.register(self.solver)
      self.solver.call("outputs", "disable")
      self.outputs.disable()

   def run(self, instance: Any, strategy: Any) -> str:
      """Read and return the cached raw output for `(instance, strategy)`."""
      # triggers Time.decorate() to snapshot start time; no subprocess is launched
      self.decorate("", instance, strategy)
      try:
         return self.outputs.read(instance, strategy)
      except FileNotFoundError:
         logger.warning(f"No cached output for {instance} / {strategy}")
         return ""

   def process(self, output: str) -> "Result":
      """Delegate output parsing to the wrapped solver."""
      return self.solver.process(output)

   def valid(self, result: "Result") -> bool:
      """Delegate result validation to the wrapped solver."""
      return self.solver.valid(result)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      """Delegate command decoration to the wrapped solver."""
      return self.solver.decorate(cmd, instance, strategy)

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      """Delegate result update/announcement to the wrapped solver."""
      self.solver.update(instance, strategy, output, result)

   def translate(
      self,
      instance: Any,
      strategy: Any,
   ) -> tuple[Any, Any]:
      """Delegate instance/strategy translation to the wrapped solver."""
      return self.solver.translate(instance, strategy)

   @property
   def name(self) -> str:
      """Reloader name including the wrapped solver name, e.g. `Reloader(E:T10)`."""
      return f"{super().name}({self.solver.name})"

   @property
   def success(self) -> frozenset[str]:
      """Delegate to the wrapped solver's success statuses."""
      return self.solver.success

   @property
   def timeouts(self) -> frozenset[str]:
      """Delegate to the wrapped solver's timeout statuses."""
      return self.solver.timeouts

