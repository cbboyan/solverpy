from ..decorator import Decorator
from ..translator import Translator

def build(fun, arg):
   return fun % arg if isinstance(fun, str) else fun(arg)

class Limits(Decorator, Translator):
   """
   This is either a decorator or a translator based on the value
   of `cmdline`.
   """

   def __init__(self, limit, builder, cmdline=True):
      lims = {x[0]:x[1:] for x in limit.split("-") if x}
      self.timeout = int(lims["T"]) if "T" in lims else None
      self.memory = float(lims["M"]) if "M" in lims else None
      try:
         lims = [build(builder[x],y) for (x,y) in lims.items() if x in builder]
      except Exception as e:
         print(e)
         raise Exception(f"solverpy: Invalid limit string: {limit}")

      delim = " " if cmdline else ""
      self.strat = delim.join(lims)
      self.cmdline = cmdline

      #self.args = " ".join(lims)
      self.limit = limit
   
   def register(self, solver):
      solver.translators.append(self)
      solver.decorators.append(self)

   def __repr__(self):
      return f"{type(self).__name__}({repr(self.limit)})"

   def __str__(self):
      return self.limit

   def __lt__(self, other):
      if self.limit and not other.limit:
         return None
      if self.memory and not other.memory:
         return None
      if not self.memory:
         return (self.timeout < other.timeout) 
      else:
         return (self.timeout < other.timeout) or (self.memory < other.memory)
   
   #def __le__(self, other):
   #   return (self.key == other.key) or (self < other)

   def decorate(self, cmd):
      if self.cmdline:
         return f"{cmd} {self.strategy}" if self.strategy else cmd
      else:
         return cmd

   def translate(self, instance, strategy):
      if not self.cmdline:
         return (instance, self.strategy + strategy)
      else:
         return (instance, strategy)
  
   @property
   def strategy(self):
      return self.strat
   
