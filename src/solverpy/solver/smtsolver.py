from .shellsolver import ShellSolver
from .plugins.status.smt import Smt
from .plugins.shell.time import Time

SMT_OK = frozenset([
   'sat', 
   'unsat',
])

SMT_FAILED = frozenset([
   'unknown', 
   'timeout',
   'TIMEOUT', # simulated timeout
])

SMT_ALL = SMT_OK | SMT_FAILED

class SmtSolver(ShellSolver):

   def __init__(self, cmd, limit, builder={}, plugins=[], wait=None):
      plugins = plugins + [ Time(), Smt() ] 
      ShellSolver.__init__(self, cmd, limit, builder, plugins, wait)

   def valid(self, result):
      return super().valid(result) and result["status"] in SMT_ALL

   def solved(self, result):
      return ("status" in result) and (result["status"] in SMT_OK)

   def permanent(self, result):
      return result["status"] in SMT_OK

