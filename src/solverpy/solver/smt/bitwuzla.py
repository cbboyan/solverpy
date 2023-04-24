import re
from ..smtsolver import SmtSolver
from ...tools import patterns, human

BWZ_BINARY = "bitwuzla"

BWZ_STATIC = "-v"

BWZ_BUILDER = {
   "T": "-t=%s",
}

BWZ_TABLE = {
   "variable substitutions"               : "SubstVar",
   "uninterpreted function substitutions" : "SubstUf",
   "embedded constraint substitutions"    : "SubstEc",
   "AIG vectors"                          : "AigVec",
   "AIG ANDs"                             : "AigAnd",
   "AIG variables"                        : "AigVar",
   "CNF variables"                        : "CnfVar",
   "CNF clauses"                          : "CnfCls",
   "CNF literals"                         : "CnfLit",
   "cached (add)"                         : "RwcAdd",
   "cached (get)"                         : "RwcGet",
   "udpated"                              : "RwcUpd",
}

BWZ_KEYS = "|".join(BWZ_TABLE.keys()).replace("(","[(]").replace(")","[)]")

#BWZ_PAT = re.compile(r"^\[bitwuzla>core\]\s*(\d+) ([a-zA-Z ]*)\b", flags=re.MULTILINE)
BWZ_PAT = re.compile(r"^\[bitwuzla>core\]\s*(\d+) (%s)" % BWZ_KEYS, flags=re.MULTILINE)

class Bitwuzla(SmtSolver):
   
   def __init__(self, limit, binary=BWZ_BINARY, static=BWZ_STATIC, plugins=[]):
      cmd = f"{binary} {static}"
      SmtSolver.__init__(self, cmd, limit, BWZ_BUILDER, plugins, wait=1)

   def process(self, output):
      result = patterns.valkey(BWZ_PAT, output, BWZ_TABLE)
      result = patterns.mapval(result, human.numeric)
      return result

