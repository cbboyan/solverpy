from .pluginsolver import PluginSolver

class TimedSolver(PluginSolver):
   
   def __init__(self, timeout, plugins=[]):
      self.timeout = timeout
      PluginSolver.__init__(self, plugins)

   def permanent(self, result):
      raise NotImlementedError()
   
   def applicable(self, result):
      if self.permanent(result):
         # permanent result always allows to predict correctly
         return True
      else:
         # recompute (False) if we have more time than last runtime
         return result["runtime"] > self.timeout

   def simulate(self, result):
      if self.permanent(result):
         if result["runtime"] > self.timeout:
            # the status is permanent, but we don't have enough time
            return dict(result, status="TIMEOUT", runtime=self.timeout)
      else:
         if result["runtime"] <= self.timeout:
            # the result needs to be recomputed since we have more time now
            return None
      return result # the result is already up-to-date

   def query(self, instatance, strategy):
      result = super().query(instatance, strategy)
      if result: # the result of query is always applicable (or None)
         result = self.simulate(result) 
      return result

