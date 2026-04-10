from solverpy.solver.smt.cvc5 import Cvc5, CVC5_BINARY, CVC5_STATIC

from .solverpy import SolverPyRunner
from ..trainer.cvc5.domain import DEFAULTS, CONDITIONS


class Cvc5Runner(SolverPyRunner):

   RESOURCE_KEY = "resource::resourceUnitsUsed"

   def __init__(self, config={}):
      SolverPyRunner.__init__(self, config)
      self.default("penalty", 100000000)
      self.conds = self.conditions(CONDITIONS)
      binary = self.config.get("cbinary") or CVC5_BINARY
      static = self.config.get("cargs") or CVC5_STATIC
      limit = self.config["timeout"]
      if "rlimit" in self.config:
         limit = f"T{limit}-R{self.config['rlimit']}"
      else:
         limit = f"T{limit}"
      self._solver = Cvc5(limit=limit, binary=binary, static=static)

   def args(self, params):
      def one(arg, val):
         arg = arg.replace("_", "-")
         val = val.replace("_", "-")
         if val == "yes":
            return f"--{arg}"
         elif val == "no":
            return f"--no-{arg}"
         else:
            return f"--{arg}={val}"
      return " ".join([one(x, params[x]) for x in sorted(params)])

   def clean(self, params):
      # remove default values
      params = {x: params[x] for x in params if params[x] != DEFAULTS[x]}
      # remove conditioned params whose conditions are not met
      delme = set()
      idle = False
      while not idle:
         idle = True
         for x in params:
            if x not in self.conds:
               continue
            for y in self.conds[x]:
               val = params[y] if y in params else DEFAULTS[y]
               if val not in self.conds[x][y]:
                  delme.add(x)
                  break
         for x in delme:
            del params[x]
            idle = False
         delme.clear()
      return params
