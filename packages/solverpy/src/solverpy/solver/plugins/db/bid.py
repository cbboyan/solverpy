from typing import Any

from ..translator import Translator
from ....benchmark.path import bids

class Bid(Translator):
   """Translate a `(bid, problem)` instance pair to the full problem file path.

   The instance passed into the solver during benchmark evaluation is a tuple
   `(bid, problem)` where `bid` is a benchmark directory id and `problem` is a
   relative problem name within that benchmark.  This translator unwraps the
   tuple and resolves it to an absolute file path via
   [`bids.path`][solverpy.benchmark.path.bids.path].

   `Bid` must run **before** `Sid` in the translator chain (the default order
   established by [`plugins.db()`][solverpy.solver.plugins.db]).
   """

   def __init__(self, **kwargs):
      Translator.__init__(self, **kwargs)

   def translate(
      self,
      instance: tuple[str, str],
      strategy: Any
   ) -> tuple[str, Any]:
      """Resolve `(bid, problem)` → absolute file path."""
      (bid, problem) = instance
      instance0 = bids.path(bid, problem)
      return (instance0, strategy)

