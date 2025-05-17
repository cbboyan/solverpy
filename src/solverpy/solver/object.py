import logging

logger = logging.getLogger(__name__)

class SolverPyObj:

   def __init__(self, myname:(str|None)=None, **kwargs):
      self._repr_args : (dict|None) = dict(kwargs)
      self._myname = myname or self.__class__.__name__

   def __repr__(self) -> str:
      if hasattr(self, "_repr_args") and self._repr_args is not None:
         ias = [f"{x}={y}" for (x,y) in self._repr_args.items()]
         ias = ",".join(sorted(ias))
         return f"{self._myname}({ias})"
      return object.__repr__(self)

   def represent(self) -> (str|list|tuple|dict):
      """Default yaml represeneter"""
      return repr(self)

