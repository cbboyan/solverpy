from ..decorator import Decorator

class Limiter(Decorator):

   def register(self, solver):
      super().register(solver)
      self.timeouts = solver.timeouts
      self.timeout = solver.limits.timeout
      self.limit = solver.limits.limit
   
   def update(self, instance, strategy, output, result):
      if (not result) or ("status" not in result) or ("runtime" not in result):
         return
      if (result["status"] in self.timeouts) or \
            (result["runtime"] > self.timeout):
         result["runtime"] = self.timeout
      result["limit"] = self.limit
         

