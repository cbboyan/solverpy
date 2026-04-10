from solverpy.solver.smt.z3 import Z3

from .solverpy import SolverPyRunner
from .config import Params, RunnerConfig
from ..trainer.z3.options import OptionsDomain
from ..trainer.z3.tactics import TACTICS, BOOLS, DEPTHS


def options(params: Params, i: int, name: str, typ: str, defs: dict[str, list[str]]) -> list[str]:
   if name not in defs:
      return []
   opts = []
   for (n, arg) in enumerate(defs[name]):
      param = f"t__t{i}__{typ}{n}"
      assert param in params
      opts.append(f":{arg} {params[param]}")
   return opts

def tactic(params: Params, i: int) -> str:
   master = f"t__t{i}"
   assert master in params
   name = TACTICS[int(params[master])]
   opts: list[str] = []
   opts.extend(options(params, i, name, "bool", BOOLS))
   opts.extend(options(params, i, name, "depth", DEPTHS))
   if opts:
      return f"(or-else (using-params {name} {' '.join(opts)}) skip)"
   else:
      return f"(or-else {name} skip)"

def tactical(params: Params) -> str | None:
   if "t__count" not in params:
      return None
   n_count = int(params["t__count"])
   ts = []
   for i in range(n_count):
      ts.append(tactic(params, i))
   if not ts:
      return None
   ts.append("smt")
   return f"(then {' '.join(ts)})"

class Z3Runner(SolverPyRunner):

   RESOURCE_KEY = "rlimit-count"

   def __init__(self, config: RunnerConfig = RunnerConfig()):
      SolverPyRunner.__init__(self, config)
      self.default("penalty", 100000000)
      assert "penalty" in self.config
      self.default("penalty.error", self.config["penalty"] * 1000)  # type: ignore[literal-required]
      self.default_domain(OptionsDomain)

      assert "timeout" in self.config
      limit = self.config["timeout"]
      self.setup(Z3(limit=f"T{limit}-M4", complete=False))

   def args(self, params: Params) -> str:
      opts = []
      for x in params:
         if not x.startswith("t__"):
            opts.append(f"(set-option :{x} {params[x]})")
      options = "\n".join(opts)
      assert self.domain
      tac = tactical(self.domain.defaults | params)
      if tac is None:
         return options
      else:
         return f"{options}\n\n;(check-sat-using {tac})"
   
