from typing import Any, TYPE_CHECKING
from ..decorator import Decorator

if TYPE_CHECKING:
   from ...solverpy import SolverPy
   from ....tools.typing import Result

TIMEOUT_CMD = "timeout --kill-after=15 --foreground %s"


class Timeout(Decorator):
   """Enforce a hard wall-clock cutoff using the GNU `timeout` command.

   Prepends `timeout --kill-after=15 --foreground <N>` to the solver command.
   If the solver does not finish within `N` seconds, `timeout` sends `SIGTERM`;
   after a further 15 seconds it sends `SIGKILL`.

   This decorator inserts itself at **position 0** so it becomes the outermost
   wrapper — it fires before any other decorator modifies the command.

   In `update()` it sets `result["status"] = "TIMEOUT"` when the subprocess
   exits with code 124 (killed by `timeout`) or 137 (killed by `SIGKILL`).
   """

   def __init__(self, timeout: int):
      """Args:
         timeout: Wall-clock limit in seconds.
      """
      Decorator.__init__(self, timeout=timeout)
      self.timeout = timeout
      self.prefix = TIMEOUT_CMD % timeout

   def register(self, solver: "SolverPy") -> None:
      """Insert at position 0 of `solver.decorators` (outermost wrapper)."""
      self.solver = solver
      solver.decorators.insert(0, self)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      """Prepend the `timeout` command to *cmd*."""
      del instance, strategy # unused arguments
      return f"{self.prefix} {cmd}"

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      """Set `status = "TIMEOUT"` if the process was killed by the timeout."""
      del instance, strategy, output # unused arguments
      if self.solver._exitcode in [124, 137]:
         # killed by timeout or SIGKILL
         result["status"] = "TIMEOUT"

