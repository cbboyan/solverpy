from typing import Any, Iterable, TYPE_CHECKING
import hashlib
import json

from ..decorator import Decorator

if TYPE_CHECKING:
   from ....tools.typing import Result
   from ...solverpy import SolverPy


def runhash(res: "Result") -> int:
   """Compute the runhash of a dict of result values: a short, deterministic
   fingerprint.

   `res` is JSON-serialized with sorted keys and no incidental whitespace, so
   two dicts with the same keys and values always produce the same runhash
   regardless of insertion order. Truncated to 8 bytes (64 bits) of SHA-256 --
   collisions are not a concern here, since the runhash is used to *notice*
   equal runs among a handful of candidates, not as a cryptographic or
   globally-unique id.

   Returned as a plain integer rather than a hex string: it is used as a
   number everywhere it is consumed (XOR-combined across a batch, compared
   for equality), and `result["runhash"]` round-trips through `json.dumps` as
   a bare number just as well as any other numeric result field. Format it as
   `f"{h:016x}"` at the point it needs to look like a fingerprint (a log line,
   the wrapper's result-line field) rather than storing it pre-formatted.

   Args:
      res: A JSON-serializable dict, typically a subset of a solver's result.

   Returns:
      The runhash, as an unsigned 64-bit integer (`0` to `2**64 - 1`).
   """
   data = json.dumps(
      res,
      sort_keys=True,
      separators=(",", ":"),
      ensure_ascii=False,
   ).encode("utf-8")

   return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")


class RunHash(Decorator):
   """Compute a runhash for each run, capturing the solver's internal
   behaviour independent of its options.

   Hashes a fixed subset of `result` -- the solver's own internal counters
   (e.g. decisions, propagations, preprocessing pass counts), not wall-clock
   time or its command-line options -- into `result["runhash"]` via
   [`runhash`][solverpy.solver.plugins.status.runhash.runhash].

   Two runs of the *same instance* that produce the same runhash did
   byte-identical work internally, even if they were launched with different
   strategies. That makes the runhash a cheap way to catch an option that
   parses, reaches the command line, and is reachable, yet changes nothing
   about what the solver actually does (an "inert" parameter) -- a failure
   mode that a plateau in the score alone cannot distinguish from a
   genuinely flat region of the search space.

   Which keys count as "internal behaviour" is solver-specific and supplied
   by the caller as `gens`; see `PRIMO_RUNHASH_GEN` in
   [`Primo`][solverpy.solver.smt.primo.Primo] for the primo selection.
   """

   def __init__(self, gens: Iterable[str], **kwargs: Any):
      """Args:
         gens: An iterable of `result` keys to include in the runhash. Keys
            not present in `result` for a given run are simply skipped, so
            the same `gens` works across instances that populate different
            subsets of counters (e.g. a problem solved during preprocessing
            never emits `sat.*` keys).
      """
      self._gens = gens
      Decorator.__init__(self, **kwargs)

   def selected(self, key: str) -> bool:
      """Return whether result key `key` is included in the runhash."""
      return key in self._gens

   def register(self, solver: "SolverPy") -> None:
      """Append to decorators. Does not touch the solver's status sets."""
      super().register(solver)

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      """Compute the runhash of the selected subset of `result` and write it
      to `result["runhash"]`."""
      del instance, strategy, output  # unused arguments
      #runhash = {x:result[x] for x in result if not x.endswith("-us")}
      sels = {k: result[k] for k in result if self.selected(k)}
      result["runhash"] = runhash(sels)
