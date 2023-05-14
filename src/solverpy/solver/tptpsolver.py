from .shellsolver import ShellSolver
from .plugins.status.tptp import Tptp
from .plugins.shell.time import Time

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
   "TIMEOUT", # simulated timeout
])

TPTP_INCOMPLETE = frozenset([
   'Satisfiable', 
   'CounterSatisfiable', 
])

TPTP_ALL = TPTP_OK | TPTP_FAILED | TPTP_TIMEOUT

INC_OK = TPTP_OK - TPTP_INCOMPLETE

class TptpSolver(ShellSolver):

   def __init__(self, cmd, limit, builder={}, plugins=[], wait=None, complete=True, name=None):
      plugins = plugins + [ Time(), Tptp() ] 
      ShellSolver.__init__(self, cmd, limit, builder, plugins, wait, name=name)
      self.complete = complete

   def valid(self, result):
      return super().valid(result) and result["status"] in TPTP_ALL

   @property
   def success(self):
      return TPTP_OK if self.complete else INC_OK

   @property
   def timeout(self):
      return TPTP_TIMEOUT

