import re
from ..smtsolver import SmtSolver
from ...tools import patterns, human

CVC5_BINARY = "cvc5"

CVC5_STATIC = "--produce-proofs --dump-instantiations --print-inst-full " +\
              "--stats --stats-internal --track-relevant-literals"

CVC5_BUILDER = {
   "T": lambda x: "--tlimit=%s" % (1000*int(x)),
   "R": lambda x: "--rlimit=%s" % x
}

CVC5_KEYS = [
   "driver::totalTime",
   "resource::resourceUnitsUsed",
   "resource::steps::resource",
   "Instantiate::[^ ]*",
   "SharedTermsDatabase::termsCount",
   "sat::conflicts",
   "sat::decisions",
   "sat::clauses_literals",
   "sat::propagations",
]

CVC5_PAT = re.compile(r"^(%s) = (.*)$" % "|".join(CVC5_KEYS), flags=re.MULTILINE)

CVC5_TIMEOUT = re.compile(r"cvc5 interrupted by (timeout)")

class Cvc5(SmtSolver):
   
   def __init__(self, limit, binary=CVC5_BINARY, static=CVC5_STATIC, plugins=[]):
      cmd = f"{binary} {static}"
      SmtSolver.__init__(self, cmd, limit, CVC5_BUILDER, plugins, wait=1)
   
   def process(self, output):
      
      def parseval(val):
         if val.startswith("{") and val.endswith("}"):
            val = val.strip(" {}")
            val = val.split(",")
            val = [x.split(":") for x in val]
            return {x.strip():human.numeric(y.strip()) for (x,y) in val}
         return human.numeric(val)
      
      result = patterns.keyval(CVC5_PAT, output)
      result = patterns.mapval(result, parseval)
      timeouted = patterns.single(CVC5_TIMEOUT, output, None)
      if timeouted:
         result["status"] = timeouted
      return result
   
