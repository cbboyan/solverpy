from ..translator import Translator
from ....benchmark.path import sids

class Sid(Translator):
   "Strategy ids translator."

   def __init__(self, unspace=True):
      self.unspace = unspace
   
   def translate(self, instance, strategy):
      sid = strategy
      strategy = sids.load(sid)
      if self.unspace:
         strategy = sids.unspace(strategy)
      if "@@@" in strategy:
         (sid, args) = sids.split(sid)
         strategy = sids.instatiate(strategy, args)
      return (instance, strategy)

