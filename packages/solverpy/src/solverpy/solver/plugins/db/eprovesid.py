from typing import Any

from ..translator import Translator
from ....benchmark.path import sids


class EProverSid(Translator):
   """Sid translator for E Prover supporting both old and new strategy formats.

   Old format (CLI options string): behaves identically to
   [`Sid`][solverpy.solver.plugins.db.sid.Sid] — loads the file contents and
   returns them as the strategy string.

   New format (file starts with `{`): the file contains an E Prover strategy
   block produced by `--print-strategy`.  In this case the file path is passed
   to E via `--parse-strategy=<path>` instead of inlining the options.

   Parametric strategies (`@@@`) are not supported for new-format esids.
   """

   def translate(
      self,
      instance: Any,
      strategy: str,
   ) -> tuple[Any, str]:
      """Load strategy and return CLI options or `--parse-strategy=<path>`."""
      strategy0 = sids.load(strategy)
      if strategy0.startswith("{"):
         assert "@@@" not in strategy0, \
            f"Parametric strategies not supported for esid: {strategy}"
         return (instance, f"--parse-strategy={sids.path(strategy)}")
      return (instance, sids.resolve(strategy, strategy0))
