from solverpy.solver.atp.vampire import Vampire, V_BINARY, V_STATIC

from .solverpy import SolverPyRunner
from .config import Params, RunnerConfig
from ..trainer.vampire.full import DEFAULTS, REPLACE


class VampireRunner(SolverPyRunner):

   RESOURCE_KEY = "Active"

   def __init__(self, config: RunnerConfig = RunnerConfig()):
      SolverPyRunner.__init__(self, config)
      self.default("penalty", 100000000)
      binary = self.config.get("vbinary") or V_BINARY
      static = self.config.get("vargs") or V_STATIC
      assert "timeout" in self.config
      limit = self.config["timeout"]
      self.setup(Vampire(limit=f"T{limit}", binary=binary, static=static))

   def args(self, params: Params) -> str:
      def one(arg: str, val: str) -> str:
         if val.startswith("__"):
            val = val[2:]
         if arg in REPLACE:
            val = val.replace("_", REPLACE[arg])
         return f"--{arg} {val}"
      return " ".join([one(x, params[x]) for x in sorted(params)])

   def clean(self, params: Params) -> Params:
      return {x: params[x] for x in params if params[x] != DEFAULTS[x]}
