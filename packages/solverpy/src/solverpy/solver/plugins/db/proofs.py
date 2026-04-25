import os
import re
import gzip
from typing import TYPE_CHECKING

from ..decorator import Decorator
from ....benchmark.path import bids, sids

if TYPE_CHECKING:
   from ...solverpy import SolverPy

_SZS_PAT = re.compile(
   r"(% SZS output start[^\n]*\n.*?% SZS output end[^\n]*)",
   re.DOTALL,
)
_FILE_PAT = re.compile(r"file\([^,]+,\s*([^)]+)\)")


def _szs_block(output: str) -> str | None:
   """Return the full SZS proof block (including markers), or ``None``."""
   m = _SZS_PAT.search(output)
   return m.group(1) if m else None


def _names_from_block(block: str) -> list[str]:
   seen: set[str] = set()
   names: list[str] = []
   for name in _FILE_PAT.findall(block):
      name = name.strip()
      if name not in seen:
         seen.add(name)
         names.append(name)
   return names


def extract(output: str) -> list[str]:
   """Extract unique TPTP formula names from a TPTP proof output.

   Scans the block between ``SZS output start`` and ``SZS output end`` for
   ``file(<filename>, <name>)`` annotations and returns the deduplicated list
   of formula names in first-occurrence order.
   """
   block = _szs_block(output)
   return _names_from_block(block) if block else []


def _write_plain(path: str, content: str) -> None:
   os.makedirs(os.path.dirname(path), exist_ok=True)
   with open(path, "w") as f:
      f.write(content)


def _write_gz(path: str, content: str) -> None:
   os.makedirs(os.path.dirname(path), exist_ok=True)
   with gzip.open(path + ".gz", "wb") as f:
      f.write(content.encode())


class Proofs(Decorator):
   """Write TPTP proof and/or premise names to ``solverpy_db/`` subdirectories.

   Fires whenever the solver output contains an SZS proof block (between
   ``% SZS output start`` and ``% SZS output end``), regardless of the result
   dict.  Requires the instance to be a ``(bid, problem)`` tuple (i.e. used
   together with :class:`~solverpy.solver.plugins.db.bid.Bid`).

   Directory structure mirrors
   :class:`~solverpy.solver.plugins.db.outputs.Outputs`:
   ``solverpy_db/{proofs,premises}/<bid+limit>/<sid>/<problem>``.

   Args:
      proof: Write the raw proof block to ``solverpy_db/proofs/<bid+limit>/<sid>/<problem>``.
      premises: Write deduplicated formula names (one per line) from
         ``file(<filename>, <name>)`` annotations to
         ``solverpy_db/premises/<bid+limit>/<sid>/<problem>``.
      flatten: Replace ``/`` in problem paths with ``_._`` (or a custom
         string) so all files live in a single flat directory.
      compress: Gzip-compress proof files (appends ``.gz``).  Premises files
         are never compressed.
      pid: Plugin id for use with ``solver.call()``.
   """

   def __init__(
      self,
      proof: bool = True,
      premises: bool = False,
      flatten: bool | str = True,
      compress: bool = True,
      pid: str = "proofs",
   ):
      Decorator.__init__(
         self,
         proof=proof,
         premises=premises,
         flatten=flatten,
         compress=compress,
         pid=pid,
      )
      self._proof = proof
      self._premises = premises
      self._flatten = flatten
      self._compress = compress
      self._proofs_path = bids.dbpath("proofs")
      self._premises_path = bids.dbpath("premises")
      self._limit: str = ""

   def register(self, solver: "SolverPy") -> None:
      solver.decorators.append(self)
      self._limit = solver._limits.limit

   def proof_path(self, instance: tuple[str, str], strategy: str) -> str:
      """Return the proof file path (without ``.gz`` when compress is on)."""
      (bid, problem) = instance
      if self._flatten:
         sep = "_._" if self._flatten is True else self._flatten
         problem = problem.replace("/", sep)
      return os.path.join(
         self._proofs_path,
         bids.name(bid, limit=self._limit),
         sids.name(strategy),
         problem,
      )

   def premises_path(self, instance: tuple[str, str], strategy: str) -> str:
      """Return the premises file path."""
      (bid, problem) = instance
      if self._flatten:
         sep = "_._" if self._flatten is True else self._flatten
         problem = problem.replace("/", sep)
      return os.path.join(
         self._premises_path,
         bids.name(bid, limit=self._limit),
         sids.name(strategy),
         problem,
      )

   def finished(
      self,
      instance,
      strategy: str,
      output: str,
      result: dict,
   ) -> None:
      if not self._enabled:
         return
      if not isinstance(instance, tuple):
         return
      block = _szs_block(output or "")
      if not block:
         return
      if self._proof:
         p = self.proof_path(instance, strategy)
         if self._compress:
            _write_gz(p, block)
         else:
            _write_plain(p, block)
      if self._premises:
         names = _names_from_block(block)
         if names:
            _write_plain(self.premises_path(instance, strategy),
                         "\n".join(sorted(names)) + "\n")
