from typing import TYPE_CHECKING
import re

from ..tptpsolver import TptpSolver
from ...tools import patterns, human

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import LimitBuilder, Result

E_BINARY = "eprover"

E_STATIC: str = "-s -p -R --print-statistics --tstp-format --memory-limit=2048"

E_BUILDER: "LimitBuilder" = {
   "T": lambda x: "--soft-cpu-limit=%s --cpu-limit=%s" % (x, int(x) + 10),
   "P": "--processed-set-limit=%s",
   "C": "--processed-clauses-limit=%s",
   "G": "--generated-limit=%s"
}

E_PAT = re.compile(r"^#\s*(\S.*\S)\s*: (\S*)$", re.MULTILINE)

E_TABLE = {
   "Processed clauses": "Processed",
   "Generated clauses": "Generated",
   "Proof object total steps": "ProofLen",
   "Removed by relevancy pruning/SinE": "Pruned",
   "Backward-subsumed": "BackSub",
   "Backward-rewritten": "BackRew",
   "Paramodulations": "Paramod",
   "Factorizations": "Fact",
   "Equation resolutions": "EqRes",
   "Clause-clause subsumption calls (NU)": "Subsumes",
   "Termbank termtop insertions": "TermBank",
}


class E(TptpSolver):

   def __init__(
      self,
      limit: str,
      binary: str = E_BINARY,
      static: str = E_STATIC,
      complete: bool = True,
      plugins: list["Plugin"] = [],
   ):
      cmd = f"{binary} {static}"
      TptpSolver.__init__(
         self,
         cmd,
         limit,
         E_BUILDER,
         plugins,
         15,
         complete,
      )

   def process(self, output: str) -> "Result":
      result = patterns.keyval(E_PAT, output, E_TABLE)
      result = patterns.mapval(result, human.numeric)
      return result

