import os

from .. import log
from .runner import GrackleRunner


class SolverPyRunner(GrackleRunner):
   """Base runner for solverpy-backed solvers.

   Subclasses must set `self._solver` (a solverpy solver instance) in
   `__init__` and implement `args(params)`.  Override `RESOURCE_KEY` to
   pull a solver-specific resource counter from the result dict.
   """

   RESOURCE_KEY = None

   def run(self, entity, inst):
      params = entity if self.config["direct"] else self.recall(entity)
      strat = self.args(params)
      problem = os.path.join(os.getenv("SOLVERPY_BENCHMARKS", "."), inst)
      try:
         result = self._solver.solve(problem, strat)
      except Exception:
         result = {}
      if not self._solver.valid(result):
         msg = "\nERROR(Grackle): Error while evaluating on instance %s!\nstrategy: %s\nparams: %s\noutput: \n%s\n" % (
            inst, strat, self.repr(params), getattr(self._solver, "_output", "")
         )
         log.fatal(msg)
         return None
      ok = self._solver.solved(result)
      status = result["status"]
      runtime = result["runtime"]
      quality = 10 + int(1000 * runtime) if ok else self.config["penalty"]
      resources = result.get(self.RESOURCE_KEY, quality) if self.RESOURCE_KEY else quality
      return [quality, runtime, status, resources]

   def success(self, result):
      return result in self._solver.success
