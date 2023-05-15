from .shellsolver import ShellSolver
from .plugins.status.smt import Smt
from .plugins.shell.time import Time

SMT_OK = frozenset([
   'sat', 
   'unsat',
])

SMT_FAILED = frozenset([
   'unknown', 
])

SMT_TIMEOUT = frozenset([
   'timeout',
   'TIMEOUT', # simulated timeout
])

SMT_ALL = SMT_OK | SMT_FAILED | SMT_TIMEOUT

class SmtSolver(ShellSolver):

   def __init__(self, cmd, limit, builder={}, plugins=[], wait=None):
      plugins = plugins + [ Time(), Smt() ] 
      ShellSolver.__init__(self, cmd, limit, builder, plugins, wait)

   def valid(self, result):
      return super().valid(result) and result["status"] in SMT_ALL

   @property
   def success(self):
      return SMT_OK
   
   @property
   def timeouts(self):
      return SMT_TIMEOUT

