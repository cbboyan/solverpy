import re
from ..smtsolver import SmtSolver
from ..plugins.shell.limits import Limits
from ...tools import patterns, human

Z3_BINARY = "z3"

Z3_STATIC = "-smt2 -st"

Z3_BUILDER = {
   "T": "-T:%s",
   "M": "-memory:%s",
}

Z3_PAT = re.compile(r"^.:([a-z-]*)\s*([0-9.]*)", flags=re.MULTILINE)

class Z3(SmtSolver):
   
   def __init__(self, limit, binary=Z3_BINARY, static=Z3_STATIC, plugins=[]):
      cmd = f"{binary} {static}"
      SmtSolver.__init__(self, cmd, limit, Z3_BUILDER, plugins, 1)

   def process(self, output):
      result = patterns.keyval(Z3_PAT, output)
      result = patterns.mapval(result, human.numeric)
      return result

