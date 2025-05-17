from typing import Any

from ..translator import Translator
from ....benchmark.path import bids

class Bid(Translator):
   "Benchmark ids translator."

   def __init__(self, **kwargs):
      Translator.__init__(self, **kwargs)
   
   def translate(
      self, 
      instance: tuple[str,str], 
      strategy: Any
   ) -> tuple[str,Any]:
      (bid, problem) = instance
      instance0 = bids.path(bid, problem)
      return (instance0, strategy)

