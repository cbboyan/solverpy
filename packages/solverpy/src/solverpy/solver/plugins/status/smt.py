from typing import Any, TYPE_CHECKING
import re

from ..decorator import Decorator
from ....tools import patterns

if TYPE_CHECKING:
   from ....tools.typing import Result
   from ...solverpy import SolverPy

SMT_STATUS = re.compile(r"^(sat|unsat|unknown|timeout)$", re.MULTILINE)

SMT_OK = frozenset([
   'sat',
   'unsat',
])

SMT_FAILED = frozenset([
   'unknown',
])

SMT_TIMEOUT = frozenset([
   'timeout',
   'memout',
   'TIMEOUT',  # simulated timeout
])

SMT_INCOMPLETE = frozenset([
   "sat",
])

SMT_ALL = SMT_OK | SMT_FAILED | SMT_TIMEOUT

SMT_INC_OK = SMT_OK - SMT_INCOMPLETE

class Smt(Decorator):
   """Parse the SMT-LIB2 status token from solver output.

   Matches one of `sat`, `unsat`, `unknown`, or `timeout` on its own line
   and writes it to `result["status"]`.  Falls back to `"error"` if no
   token is found and `result["status"]` is not yet set.

   On `register()` it also updates the solver's status sets so that
   [`Solver.solved`][solverpy.solver.solver.Solver.solved] and
   [`Solver.valid`][solverpy.solver.solver.Solver.valid] work correctly:

   - `solver._success` ← `SMT_OK` (or `SMT_INC_OK` for incomplete solvers)
   - `solver._timeouts` ← `SMT_TIMEOUT`
   - `solver._statuses` ← `SMT_ALL`

   Used by: Cvc5, Z3, Bitwuzla.
   """

   def __init__(self, complete=True, **kwargs):
      """Args:
         complete: If `True` (default), `sat` is counted as success.  Set to
            `False` for incomplete solvers where `sat` may be unreliable.
      """
      Decorator.__init__(self, complete=complete, **kwargs)
      self._complete = complete

   def register(self, solver: "SolverPy"):
      """Append to decorators and update the solver's status sets."""
      super().register(solver)
      solver._success |= SMT_OK if self._complete else SMT_INC_OK
      solver._timeouts |= SMT_TIMEOUT
      solver._statuses |= SMT_ALL

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      del instance, strategy # unused arguments
      return cmd

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      """Extract the SMT status token and write it to `result["status"]`."""
      del instance, strategy # unused arguments
      status = patterns.single(SMT_STATUS, output, "")
      if status:
         result["status"] = status
      elif "status" not in result:
         result["status"] = "error"

