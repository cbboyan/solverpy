"""
# Base object for repr and logging

`SolverPyObj` is the root base class for all SolverPy objects. It provides
a uniform `__repr__` built from the keyword arguments passed at construction
time, and a `represent` method used for YAML serialisation.
"""

from typing import Any
import logging

logger = logging.getLogger(__name__)


class SolverPyObj:
   """Root base class for all SolverPy objects providing uniform repr and YAML serialisation."""

   def __init__(
      self,
      cls_name: (str | None) = None,
      **kwargs: Any,
   ):
      """
      Args:
          cls_name: override the class name used in `repr`. Defaults to `self.__class__.__name__`.
          **kwargs: keyword arguments stored for use in `__repr__`.
      """
      self._repr_args: dict[str, Any] = dict(kwargs)
      self._cls_name = cls_name or self.__class__.__name__

   def __repr__(self) -> str:
      """Return `ClassName(key=value,...)` built from the kwargs passed at construction."""
      if hasattr(self, "_repr_args") and self._repr_args is not None:
         ias = [f"{x}={y}" for (x, y) in self._repr_args.items()]
         ias = ",".join(sorted(ias))
         return f"{self._cls_name}({ias})"
      return object.__repr__(self)

   def represent(self) -> (str | list[Any] | dict[str, Any]):
      """Default yaml represeneter"""
      return repr(self)

