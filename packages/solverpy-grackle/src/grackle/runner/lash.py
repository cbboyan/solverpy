from os import getenv
from solverpy.solver.atp.lash import Lash, L_BINARY

from .solverpy import SolverPyRunner
from ..trainer.lash.domain import DEFAULTS


class LashRunner(SolverPyRunner):

   RESOURCE_KEY = "Steps"

   def __init__(self, config={}):
      SolverPyRunner.__init__(self, config)
      self.default("penalty", 100000000)
      binary = self.config.get("lbinary") or L_BINARY
      mode_dir = getenv("LASH_MODE_DIR", "./modes")
      static = self.config.get("lstatic") or f"-p tstp -m mode0 -M {mode_dir}"
      limit = self.config["timeout"]
      self._solver = Lash(limit=f"T{limit}", binary=binary, static=static)

   def args(self, params):
      return " ".join([f"-flag {x} {params[x]}" for x in sorted(params)])

   def clean(self, params):
      return {x: params[x] for x in params if params[x] != DEFAULTS[x]}
