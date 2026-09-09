from typing import TYPE_CHECKING
import re

from ..shellsolver import ShellSolver
from ..plugins.status.runhash import RunHash
from ...tools import patterns, human
from ..plugins.status.tptp import Tptp
from ..plugins.shell.time import Time

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import LimitBuilder, Result

E_BINARY = "eprover"

E_STATIC: str = "-s -p -R --print-statistics --proof-statistics --tstp-format --memory-limit=2048"

E_BUILDER: "LimitBuilder" = {
   "T": lambda x: "--cpu-limit=%s --soft-cpu-limit=%s" % (int(x) + 10, x),
   "P": "--processed-set-limit=%s",
   "C": "--processed-clauses-limit=%s",
   "G": "--generated-limit=%s"
}

E_PAT = re.compile(r"^[#%]\s*(\S.*\S)\s*: (\S*)$", re.MULTILINE)

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

   # The proof-object block (`--proof-statistics`, added alongside `-p`):
   # only printed for a completed proof (`ProofLen` above is the same block's
   # first line), so all ten are absent -- not zero -- on anything but Theorem.
   # One headline kept per subsystem group below; the rest commented out for
   # now, uncomment when wanted.
   "Proof object clause steps": "ProofClauseSteps",
   # "Proof object formula steps": "ProofFormulaSteps",
   # "Proof object conjectures": "ProofConjectures",
   # "Proof object clause conjectures": "ProofClauseConj",
   # "Proof object formula conjectures": "ProofFormulaConj",
   # "Proof object initial clauses used": "ProofInitClauses",
   # "Proof object initial formulas used": "ProofInitFormulas",
   # "Proof object generating inferences": "ProofGenInf",
   # "Proof object simplifying inferences": "ProofSimpInf",

   # Memory/system.
   "Search garbage collected termcells": "GC",
   # "Clauses deleted for lack of memory": "MemDeleted",

   # Condensation.
   # "Condensation attempts": "CondAttempts",
   "Condensation successes": "CondSuccess",

   # Snapshot of the clause pools at cutoff, not cumulative totals.
   "Current number of processed clauses": "CurProcessed",
   # "Positive orientable unit clauses": "PosOrientable",
   # "Positive unorientable unit clauses": "PosUnorientable",
   # "Negative unit clauses": "NegUnit",
   # "Non-unit-clauses": "NonUnit",
   # "Current number of unprocessed clauses": "CurUnprocessed",
   # "Current number of archived formulas": "ArchFormulas",
   # "Current number of archived clauses": "ArchClauses",

   # SinE/propositional-encoding stats -- all zero unless that path is
   # exercised, which this workspace's benchmarks so far do not do.
   "Propositional unsat checks": "PropUnsatChecks",
   # "Propositional check models": "PropModels",
   # "Propositional check unsatisfiable": "PropUnsat",
   # "Propositional clauses": "PropClauses",
   # "Propositional clauses after purity": "PropPure",
   # "Propositional unsat core size": "PropCore",

   # Thinned sample of the remaining preprocessing/search counters.
   # "Parsed axioms": "Axioms",
   # "Removed in clause preprocessing": "PreprocRemoved",
   # "Other redundant clauses eliminated": "OtherRedundant",
   # "NegExts": "NegExts",
   "Total rewrite steps": "Rewrites",
   # "Non-unit clause-clause subsumptions": "NonUnitSubsumes",
   # "Rewrite failures with RHS unbound": "RewriteFail",
   # "BW rewrite match successes": "BWRewriteHits",
}

# Not every captured key is safe for the runhash: E can settle ties (term or
# literal orderings, or scheduling among equal-cost choices) with an internal
# nondeterminism, so two runs of the identical input can genuinely diverge --
# up to and including finding a different (still valid) proof. `Subsumes` and
# `TermBank` were caught wobbling by a handful of counts across three reruns
# of the same instance that otherwise reproduced byte-identically (same
# Processed/Generated/.../ProofLen, same proof) -- excluded here so that noise
# doesn't read as "this configuration changed something". The rest of
# `E_TABLE` reproduced exactly across those reruns and stays in -- though only
# the original eleven keys were actually checked against reruns this way; the
# proof-object/memory/condensation/snapshot/SinE/preprocessing keys added
# after them are included on the same reasoning (deterministic counters of
# completed work) but have not individually been reproduction-tested, so a
# repeat of this check may yet turn up another `Subsumes`/`TermBank`.
E_RUNHASH_GEN = frozenset(E_TABLE.values()) - {"Subsumes", "TermBank"}


class E(ShellSolver):
   """
   The `eprover` automated theorem prover for first-order logic with
   equality.

   The strategy (sid) supplies E's command-line options, appended after the
   static options (`--print-statistics --proof-statistics --tstp-format`,
   ...). TSTP-format statistics output is parsed by
   [`process`][solverpy.solver.atp.eprover.E.process]. Status is decided by
   the [`Tptp`][solverpy.solver.plugins.status.tptp.Tptp] plugin from the
   TSTP `SZS status` line.
   """

   _binary = E_BINARY

   def __init__(
      self,
      limit: str,
      binary: str = E_BINARY,
      static: str = E_STATIC,
      complete: bool = True,
      plugins: list["Plugin"] = [],
   ):
      cmd = f"{binary} {static}"
      plugins = plugins + [
         Time(),
         Tptp(complete=complete),
         RunHash(E_RUNHASH_GEN),
      ]
      ShellSolver.__init__(
         self,
         cmd,
         limit,
         E_BUILDER,
         plugins,
         15,
         complete,
         binary=binary,
      )

   def process(self, output: str) -> "Result":
      """Parse E's TSTP statistics block into a result dict."""
      result = patterns.keyval(E_PAT, output, E_TABLE)
      result = patterns.mapval(result, human.numeric)
      return result

