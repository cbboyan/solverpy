from typing import Any, Callable, TYPE_CHECKING

from .decorator import Decorator

if TYPE_CHECKING:
   from ...tools.typing import Result


class Apply(Decorator):
   """Decorator that applies a function to the result dict after each solve.

   The callable receives the current result dict and returns a dict of
   key/value pairs to merge into it.  This is a lightweight way to compute
   and store derived result keys without writing a full
   [`Decorator`][solverpy.solver.plugins.decorator.Decorator] subclass.

   The function is called during `update()`, after all earlier decorators
   have run, so keys populated by plugins registered before this one
   (e.g. `status`, `runtime`) are already available in *result*.

   Args:
      fn: Callable ``(result) -> dict`` whose return value is merged into
         *result* in place.
      **kwargs: Forwarded to :class:`Decorator`.

   Example::

      solver.init([Apply(lambda r: {"solved": r.get("status") == "Theorem"})])
   """

   def __init__(self, fn: "Callable[[Result], dict]", **kwargs: Any):
      Decorator.__init__(self, **kwargs)
      self._fn = fn

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      """Call `fn(result)` and merge the returned dict into *result*."""
      del instance, strategy, output
      result.update(self._fn(result))
