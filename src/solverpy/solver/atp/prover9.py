import re

from ..stdinsolver import StdinSolver
from ..tptpsolver import TPTP_OK, INC_OK, TPTP_ALL, TPTP_TIMEOUT
from ...tools import patterns, human
from ..plugins.shell.time import Time

P9_BINARY = "prover9"

P9_STATIC = """
clear(print_given).
clear(bell).
"""

P9_BUILDER = {
   "T": "assign(max_seconds, %s).\n",
   "M": lambda x: f"assign(max_megs, {int(x)*1000}).\n",
}

# termination reason regex pattern
P9_REASON = re.compile(r"^-+ process[^(]*\((\S*)\) -+$", 
                       flags=re.MULTILINE)

# pattern to extract all statistics
P9_STATS = re.compile(r"^=+ STATISTICS =+$(.*)^=+ end of statistics =+$", 
                      flags=re.MULTILINE|re.DOTALL)

# pattern to extract a single statistic (key/val pair)
P9_SINGLE = re.compile(r"(\w*)=([0-9.]*[0-9])")

# TPTP-compatible statuses for Prover9 termination reasons
P9_STATUS = {
   "max_seconds": "Timeout",
   "max_megs": "ResourceOut",
   "max_proofs": "Theorem",
   "sos_empty": "Satisfiable",
}

class Prover9(StdinSolver):

   def __init__(self, limit, binary=P9_BINARY, static=P9_STATIC, complete=True, plugins=[]):
      plugins = plugins + [ Time() ] 
      StdinSolver.__init__(self, binary, limit, P9_BUILDER, plugins, None, static)
      self.complete = complete

   def process(self, output):
      reason = P9_REASON.search(output)
      if not reason:
         return {}
      reason = reason.group(1)

      stats = P9_STATS.search(output)
      if stats:
         result = patterns.keyval(P9_SINGLE, stats.group(1))
      else:
         result = {}
      
      result["reason"] = reason 
      result["status"] = P9_STATUS[reason] if (reason in P9_STATUS) else reason

      result = patterns.mapval(result, human.numeric)

      if "User_CPU" in result:
         result["runtime"] = result["User_CPU"]

      return result

   def valid(self, result):
      return super().valid(result) and result["status"] in TPTP_ALL

   @property
   def success(self):
      return TPTP_OK if self.complete else INC_OK

   @property
   def timeouts(self):
      return TPTP_TIMEOUT

