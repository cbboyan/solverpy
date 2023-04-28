from ..translator import Translator
from ....benchmark.path import sids

class Sid(Translator):
   "Strategy ids translator."

   def translate(self, instance, strategy):
      sid = strategy
      strategy = sids.load(sid)
      if "@@@" in strategy:
         (sid, args) = sids.split(sid)
         strategy = sids.instatiate(strategy, args)
      return (instance, strategy)

