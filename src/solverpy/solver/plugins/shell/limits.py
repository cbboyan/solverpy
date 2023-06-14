from ..decorator import Decorator

def build(fun, arg):
   return fun % arg if isinstance(fun, str) else fun(arg)

class Limits(Decorator):

   def __init__(self, limit, builder):
      lims = {x[0]:x[1:] for x in limit.split("-") if x}
      self.timeout = int(lims["T"]) if "T" in lims else None
      self.memory = float(lims["M"]) if "M" in lims else None
      try:
         lims = [build(builder[x],y) for (x,y) in lims.items() if x in builder]
      except Exception as e:
         print(e)
         raise Exception(f"solverpy: Invalid limit string: {limit}")

      self.args = " ".join(lims)
      self.limit = limit

   def __repr__(self):
      return f"{type(self).__name__}({repr(self.limit)})"

   def __str__(self):
      return self.limit

   @property
   def key(self):
      return (self.timeout, self.memory)

   def __lt__(self, other):
      if self.limit and not other.limit:
         return None
      if self.memory and not self.memory:
         return None
      return self.key < other.key
   
   def __le__(self, other):
      return (self.key == other.key) or (self < other)

   def decorate(self, cmd):
      return f"{cmd} {self.args}" if self.args else cmd
   
