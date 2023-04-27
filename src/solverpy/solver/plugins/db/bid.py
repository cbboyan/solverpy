from ..translator import Translator
from ....benchmark.path import bids

class Bid(Translator):
   "Benchmark ids translator."
   
   def translate(self, instance, strategy):
      (bid, problem) = instance
      instance = bids.path(bid, problem)
      return (instance, strategy)

