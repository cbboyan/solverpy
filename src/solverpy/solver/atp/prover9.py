import re

from ..stdinsolver import StdinSolver
from ...tools import patterns, human

P9_BINARY = "prover9"

P9_STATIC = """
set(prolog_style_variables).
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

P9_PROVED = re.compile(r"^THEOREM PROVED$", flags=re.MULTILINE)

P9_FAILED = re.compile(r"^SEARCH FAILED$", flags=re.MULTILINE)

# TPTP compatible statuses for Prover9 termination reasons
P9_STATUS = {
   "max_seconds": "Timeout",
   "max_megs": "ResourceOut",
   "max_proofs": "Theorem",
   "sos_empty": "Satisfiable",
}

TPTP_OK = frozenset([
   'Satisfiable', 
   'Unsatisfiable', 
   'Theorem', 
   'CounterSatisfiable', 
   'ContradictoryAxioms',
])

TPTP_TIMEOUT = frozenset([
   'ResourceOut', 
   'Timeout',
   "TIMEOUT", # simulated timeout
])

class Prover9(StdinSolver):

   def __init__(self, limit, binary=P9_BINARY, static=P9_STATIC, complete=True, plugins=[]):
      StdinSolver.__init__(self, binary, limit, P9_BUILDER, plugins, None, static)

   def process(self, output):
      #if P9_PROVED.search(output):
      #   status = "Theorem"
      #elif P9_FAILED.search(output):
      #   status = None # use `reason` as status later
      #else:
      #   return dict(status="ERROR")

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
      return result

   @property
   def success(self):
      return TPTP_OK 

   @property
   def timeouts(self):
      return TPTP_TIMEOUT

