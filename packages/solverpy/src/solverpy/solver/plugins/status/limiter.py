from typing import TYPE_CHECKING, Any

from ..decorator import Decorator

if TYPE_CHECKING:
   from ...solverpy import SolverPy
   from ....tools.typing import Result


class Limiter(Decorator):
   """Cap `runtime` at the time limit and stamp `limit` onto the result.

   Two jobs in `update()`:

   1. If `result["status"]` is a timeout status *or* `result["runtime"]`
      already exceeds the time limit, clamp `result["runtime"]` to the
      limit value so that cached timeouts always report a consistent duration.
   2. Set `result["limit"]` to the limit string (e.g. `"T10"`).

   The `limit` key is **required** by
   [`SolverPy.simulate`][solverpy.solver.solverpy.SolverPy.simulate] for
   cached-result reuse under different time limits.  `Limiter` is registered
   automatically by every `SolverPy` instance, so results always carry this key.
   """

   def __init__(self, **kwargs):
      Decorator.__init__(self, **kwargs)

   def register(self, solver: "SolverPy") -> None:
      """Append to decorators and cache references to the solver's limit info."""
      super().register(solver)
      self.timeouts = solver.timeouts
      self.timeout = solver._limits.timeout
      self.limit = solver._limits.limit

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: Any,
      result: "Result",
   ) -> None:
      """Clamp `runtime` and set `result["limit"]`."""
      del instance, strategy, output # unused arguments
      if (not result) or ("status" not in result) or ("runtime" not in result):
         return
      if (result["status"] in self.timeouts) or \
            (result["runtime"] > self.timeout):
         result["runtime"] = self.timeout
      result["limit"] = self.limit

