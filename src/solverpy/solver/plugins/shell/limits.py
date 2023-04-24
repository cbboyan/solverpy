from ..decorator import Decorator

def build(fun, arg):
   return fun % arg if isinstance(fun, str) else fun(arg)

class Limits(Decorator):

   def __init__(self, limit, builder):
      lims = {x[0]:x[1:] for x in limit.split("-") if x}
      self.timeout = int(lims["T"]) if "T" in lims else None
      try:
         lims = [build(builder[x],y) for (x,y) in lims.items() if builder[x]]
      except:
         raise Exception(f"solverpy: Invalid limit string: {limit}")
      self.args = " ".join(lims)
      self.limit = limit
   
   def register(self, solver):
      super().register(solver)
      self.solver = solver
   
   def decorate(self, cmd):
      return f"{cmd} {self.args}" if self.args else cmd

   def update(self, instance, strategy, output, result):
      if not self.solver.permanent(result):
         result["timeout"] = self.timeout

