from typing import Any

from ..translator import Translator
from ....benchmark.path import sids


class Sid(Translator):
   """Load a strategy definition from `solverpy_db/strats/` by strategy id.

   The *strategy* passed into the solver during benchmark evaluation is a
   strategy id (sid) — a filename inside `solverpy_db/strats/`.  This
   translator loads the file contents (the actual solver CLI options string)
   via [`sids.load`][solverpy.benchmark.path.sids.load].

   **Parametric strategies**: if the loaded definition contains `@@@ var :
   default @@@` placeholders, the sid may carry arguments in the form
   `base_sid@var=val:var2=val2`.  The translator splits the sid, extracts the
   argument assignments, and calls
   [`sids.instatiate`][solverpy.benchmark.path.sids.instatiate] to expand the
   placeholders before returning the final strategy string.
   """

   def translate(
      self,
      instance: Any,
      strategy: str,
   ) -> tuple[Any, str]:
      """Load and (if parametric) instantiate the strategy definition."""
      sid = strategy
      strategy0 = sids.load(sid)
      if "@@@" in strategy0:
         (sid, args) = sids.split(sid)
         strategy0 = sids.instatiate(strategy0, args)
      return (instance, strategy0)

