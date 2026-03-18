from typing import Any, TYPE_CHECKING
import re

from ..decorator import Decorator
from ....tools import patterns

if TYPE_CHECKING:
   from ....tools.typing import Result
   from ...solverpy import SolverPy

TPTP_STATUS = re.compile(r"[#%] SZS status (\S*)", re.MULTILINE)

TPTP_OK = frozenset([
   'Satisfiable',
   'Unsatisfiable',
   'Theorem',
   'CounterSatisfiable',
   'ContradictoryAxioms',
])

TPTP_FAILED = frozenset([
   'GaveUp',
])

TPTP_TIMEOUT = frozenset([
   'ResourceOut',
   'Timeout',
   "TIMEOUT",  # simulated timeout
])

TPTP_INCOMPLETE = frozenset([
   'Satisfiable',
   'CounterSatisfiable',
])

TPTP_ALL = TPTP_OK | TPTP_FAILED | TPTP_TIMEOUT

TPTP_INC_OK = TPTP_OK - TPTP_INCOMPLETE

class Tptp(Decorator):
   """Parse the TPTP SZS status line from solver output.

   Matches the pattern `# SZS status <STATUS>` (or `%` prefix) in the solver
   output and writes the status token to `result["status"]`.  Falls back to
   `"ERROR"` if no status line is found and `result["status"]` is not yet set.

   On `register()` it also updates the solver's status sets so that
   [`Solver.solved`][solverpy.solver.solver.Solver.solved] and
   [`Solver.valid`][solverpy.solver.solver.Solver.valid] work correctly:

   - `solver._success` ← `TPTP_OK` (or `TPTP_INC_OK` for incomplete solvers)
   - `solver._timeouts` ← `TPTP_TIMEOUT`
   - `solver._statuses` ← `TPTP_ALL`

   Used by: E, Vampire, Lash, Prover9.
   """

   def __init__(self, complete=True, **kwargs):
      """Args:
         complete: If `True` (default), `Satisfiable` and `CounterSatisfiable`
            are counted as success.  Set to `False` for incomplete solvers
            where these statuses are unreliable.
      """
      Decorator.__init__(self, complete=complete, **kwargs)
      self._complete = complete

   def register(self, solver: "SolverPy"):
      """Append to decorators and update the solver's status sets."""
      super().register(solver)
      solver._success |= TPTP_OK if self._complete else TPTP_INC_OK
      solver._timeouts |= TPTP_TIMEOUT
      solver._statuses |= TPTP_ALL

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      del instance, strategy
      return cmd

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      """Extract the SZS status token and write it to `result["status"]`."""
      del instance, strategy
      status = patterns.single(TPTP_STATUS, output, "")
      if status:
         result["status"] = status
      elif "status" not in result:
         result["status"] = "ERROR"



