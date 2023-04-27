from ..translator import Translator
from ....benchmark.path import sids

class Sid(Translator):
   "Strategy ids translator."
   
   def translate(self, instance, strategy):
      strategy = sids.load(strategy)
      return (instance, strategy)

