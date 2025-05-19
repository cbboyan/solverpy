from typing import Any

from ..translator import Translator
from ....benchmark.path import sids


class Sid(Translator):
   "Strategy ids translator."

   def translate(
      self,
      instance: Any,
      strategy: str,
   ) -> tuple[Any, str]:
      sid = strategy
      strategy0 = sids.load(sid)
      if "@@@" in strategy0:
         (sid, args) = sids.split(sid)
         strategy0 = sids.instatiate(strategy0, args)
      return (instance, strategy0)

