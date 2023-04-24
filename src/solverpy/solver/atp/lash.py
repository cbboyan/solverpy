import re

from ..tptpsolver import TptpSolver
from ..plugins.shell.limits import Limits
from ...tools import patterns, human

L_BINARY = "lash"

#L_STATIC = "-p tstp -m mode0 -M %s" % getenv("LASH_MODE_DIR", "./modes")
L_STATIC = "-p tstp"

L_PAT = re.compile(r"^% (Steps|Mode): (\S*)$", flags=re.MULTILINE)

L_BUILDER = {
   "T": None,
}

L_TABLE = {
   "Steps": "Steps",
   "Mode": "Mode",
}

class Lash(TptpSolver):

   def __init__(self, limit, binary=L_BINARY, static=L_STATIC, complete=True, plugins=[]):
      cmd = f"{binary} {static}"
      TptpSolver.__init__(self, cmd, L_BUILDER, plugins, 0, complete)

   def process(self, output):
      result = patterns.keyval(L_PAT, output, L_TABLE)
      result = patterns.mapval(result, human.numeric)
      return result


