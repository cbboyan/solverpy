import re

from ..tptpsolver import TptpSolver
from ...tools import patterns, human

V_BINARY = "vampire"

V_STATIC = "--proof tptp -stat full --input_syntax tptp --memory_limit 2048"

V_BUILDER = {
   "T": "--time_limit %ss",
   "M": "--memory_limit %s",
}

V_PAT = re.compile(r"^% (.*): ([0-9.]*).*$", re.MULTILINE)

V_TABLE = {
   "Active clauses"    : "Active",
   "Passive clauses"   : "Passive",
   "Generated clauses" : "Generated",
   "Initial clauses   ": "Initial",
   "Time elapsed"      : "Runtime",
   "Memory used [KB]"  : "Memory",
   "Split clauses"     : "Splits",
}

class Vampire(TptpSolver):

   def __init__(self, limit, binary=V_BINARY, static=V_STATIC, complete=True, plugins=[]):
      cmd = f"{binary} {static}"
      TptpSolver.__init__(self, cmd, limit, V_BUILDER, plugins, 1, complete)

   def process(self, output):
      result = patterns.keyval(V_PAT, output, V_TABLE)
      result = patterns.mapval(result, human.numeric)
      return result

