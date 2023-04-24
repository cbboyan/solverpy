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
   'ResourceOut', 
   'GaveUp',
   'Timeout',
   "TIMEOUT", # simulated timeout
])

TPTP_INCOMPLETE = frozenset([
   'Satisfiable', 
   'CounterSatisfiable', 
])

TPTP_ALL = TPTP_OK | TPTP_FAILED

INC_OK = TPTP_OK - TPTP_INCOMPLETE

INC_FAILED = TPTP_FAILED | TPTP_INCOMPLETE


class TptpSolver(ShellSolver):

   def __init__(self, cmd, limit, builder={}, plugins=[], wait=None, complete=True):
      plugins = plugins + [ Time(), Tptp() ] 
      ShellSolver.__init__(self, cmd, limit, builder, plugins, wait)
      if complete:
         self._ok = TPTP_OK
         self._failed = TPTP_FAILED
      else:
         self._ok = INC_OK
         self._failed = INC_FAILED

   def valid(self, result):
      return super().valid(result) and result["status"] in TPTP_ALL

   def solved(self, result):
      return "status" in result and result["status"] in self._ok

   def permanent(self, result):
      return result["status"] in TPTP_OK

