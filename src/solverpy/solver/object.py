from typing import Any
import logging

logger = logging.getLogger(__name__)

class SolverPyObj:

   def __init__(self, cls_name: ( str | None ) = None, **kwargs):
      self._repr_args: dict[str, Any] = dict(kwargs)
      self._cls_name = cls_name or self.__class__.__name__

   def __repr__(self) -> str:
      if hasattr(self, "_repr_args") and self._repr_args is not None:
         ias = [f"{x}={y}" for (x,y) in self._repr_args.items()]
         ias = ",".join(sorted(ias))
         return f"{self._cls_name}({ias})"
      return object.__repr__(self)

   def represent(self) -> ( str | list[Any] | dict[str, Any]):
      """Default yaml represeneter"""
      return repr(self)

