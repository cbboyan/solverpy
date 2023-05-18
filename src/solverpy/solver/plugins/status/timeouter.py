from ..decorator import Decorator

class Timeouter(Decorator):

   def register(self, solver):
      super().register(solver)
      self.timeouts = solver.timeouts
      self.timeout = solver.timeout
   
   def update(self, instance, strategy, output, result):
      if result["status"] in self.timeouts:
         result["runtime"] = self.timeout

