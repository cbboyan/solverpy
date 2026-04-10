import os
from typing import Any, TYPE_CHECKING

from solverpy.solver.plugins.apply import Apply

from .. import log
from .runner import GrackleRunner
from .config import Params

if TYPE_CHECKING:
   from solverpy.solver.solverpy import SolverPy


class SolverPyRunner(GrackleRunner):
   """Base runner for solverpy-backed solvers.

   Subclasses construct a solverpy solver and pass it to `setup()`, which
   attaches the grackle `Apply` plugin and stores it as `self._solver`.
   Subclasses must also implement `args(params)`.

   Set `RESOURCE_KEY` to a result-dict key to pull a solver-specific resource
   counter, or override `plugin()` for custom quality/resources logic.
   """

   _solver: "SolverPy"
   RESOURCE_KEY = None

   def args(self, params: Params) -> str:
      raise NotImplementedError("Abstract method `SolverPyRunner.args` not implemented.")

   def plugin(self) -> Apply:
      """Build an Apply plugin that adds `quality` and `resources` to each result.

      All values needed to compute quality and resources are extracted as plain
      primitives here, so the resulting lambdas are fully picklable (no runner
      reference survives in the closure).
      """
      assert "penalty" in self.config
      penalty = self.config["penalty"]
      reskey = self.RESOURCE_KEY
      success = self._solver.success
      return Apply(lambda result: {
         "quality": 10 + int(1000 * result["runtime"]) if result["status"] in success else penalty,
         "resources": result[reskey] if reskey in result else 0,
      })

   def setup(self, solver: "SolverPy") -> None:
      """Store *solver* and attach the grackle quality/resources plugin."""
      self._solver = solver
      self._solver.init([self.plugin()])

   def run(self, entity: str | Params, inst: str) -> list[Any] | None:
      assert "direct" in self.config
      params: Params = entity if self.config["direct"] else self.recall(entity)  # type: ignore[assignment]
      strat = self.args(params)
      problem = os.path.join(os.getenv("SOLVERPY_BENCHMARKS", "."), inst)
      try:
         result = self._solver.solve(problem, strat)
      except Exception:
         result = {}
      if not self._solver.valid(result):
         msg = "\nERROR(Grackle): Error while evaluating on instance %s!\nstrategy: %s\nparams: %s\noutput: \n%s\n" % (
            inst, strat, params, getattr(self._solver, "_output", "")
         )
         log.fatal(msg)
         return None
      return [result["quality"], result["runtime"], result["status"], result["resources"]]

   def success(self, result: str) -> bool:
      return result in self._solver.success
