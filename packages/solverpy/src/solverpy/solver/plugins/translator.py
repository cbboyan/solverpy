from typing import Any, TYPE_CHECKING
from .plugin import Plugin

if TYPE_CHECKING:
   from ..solverpy import SolverPy

class Translator(Plugin):
   """Plugin that transforms solver inputs before each solve call.

   The single hook `translate(instance, strategy)` receives the current
   `(instance, strategy)` pair and returns a new pair.  Translators are chained
   in registration order: the output of each becomes the input of the next.

   The two built-in translators handle the benchmark database identifiers:

   - [`Bid`][solverpy.solver.plugins.db.bid.Bid] converts a `(bid, problem)`
     tuple to the full problem file path.
   - [`Sid`][solverpy.solver.plugins.db.sid.Sid] loads the strategy definition
     string from `solverpy_db/strats/`, expanding any parametric placeholders.
   """

   def __init__(self, **kwargs):
      Plugin.__init__(self, **kwargs)

   def register(self, solver: "SolverPy") -> None:
      """Append this translator to `solver.translators`."""
      solver.translators.append(self)

   def translate(
      self,
      instance: Any,
      strategy: Any
   ) -> tuple[Any, Any]:
      """Transform the `(instance, strategy)` pair.

      Args:
         instance: The current problem instance (often a `(bid, problem)` tuple
            early in the chain, a file path later).
         strategy: The current strategy value (often a sid string early in the
            chain, a full CLI options string later).

      Returns:
         A `(instance, strategy)` tuple to be passed to the next translator or,
         ultimately, to the solver's run method.  The default implementation
         returns the inputs unchanged.
      """
      return (instance, strategy)

