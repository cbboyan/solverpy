import re
from ..tptpsolver import TptpSolver
from ..smt.cvc5 import CVC5_BINARY, CVC5_STATIC, CVC5_KEYS, CVC5_BUILDER, CVC5_TIMEOUT
from ..smt.cvc5 import Cvc5 as SmtCvc5

class Cvc5(TptpSolver):
   
   def __init__(self, limit, binary=CVC5_BINARY, static=CVC5_STATIC, plugins=[], keys=CVC5_KEYS):
      cmd = f"{binary} --lang=tptp {static}"
      TptpSolver.__init__(self, cmd, limit, CVC5_BUILDER, plugins, wait=1)
      self.pattern = re.compile(r"^(%s) = (.*)$" % "|".join(keys), flags=re.MULTILINE)
   
   def process(self, output):
      result = SmtCvc5.process(self, output)
      if ("status" in result) and (result["status"] == "timeout"):
         result["status"] = "Timeout"
      return result

