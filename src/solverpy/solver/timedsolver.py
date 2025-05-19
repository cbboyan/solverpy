from .pluginsolver import PluginSolver
from .plugins.shell.limits import Limits
from .plugins.status.limiter import Limiter

# class DbSolver(PluginSolver):
# class BenchmarkSolver(PluginSolver)
# class SolverPy(PluginSolver)

class TimedSolver(PluginSolver):

   def __init__(self, timeout, limits: Limits, plugins=[]):
      self.limits = limits
      self.exitcode = None
      assert(self.limits.limit.startswith("T"))
      new = [Limiter()]
      PluginSolver.__init__(self, plugins=plugins+new)

   def __repr__(self):
      plgs = super().__repr__()
      plgs = f", plugins=[{plgs}]" if plgs else ""
      return f"{type(self).__name__}('{self.limits}'{plgs})"

   @property
   def timeouts(self):
      "The set of timeout statuses."
      raise NotImplementedError()
   
   #def recycle(self, result)
   #def reuse(self, result)
   #def determine(self, result) !!!
   def simulate(self, result):
      "Simulate run from the past result."
      if result["status"] in self.timeouts:
      #if result["status"] not in self.success: # we might want this?
         oldlimits = Limits(result["limit"], {})
         # the cached result is timeout
         if oldlimits < self.limits:
         #if result["runtime"] < self.timeout:
            # recompute since we have more time or/and space
            return None
      elif result["status"] in self.success:
         # the cached result is solved
         if result["runtime"] > self.limits.timeout:
         #if result["runtime"] > self.timeout:
            # simulated timeout
            return dict(result, 
                        status="TIMEOUT", 
                        runtime=self.limits.timeout)
      else:
         # recompute unknown results (GaveUp, unknown)
         # TODO: do we want to always recompute?
         return None
      # the result is applicable without changes
      return result

   #def simulate(self, result):
   #   "Simulate run from the past result."
   #   if result["status"] in self.timeouts:
   #      # the cached result is timeout
   #         # recompute since we have more time
   #         return None
   #   else:
   #      # the cached result is solved
   #         # simulated timeout
   #         return dict(result, 
   #                     status="TIMEOUT", 
   #                     runtime=self.timeout)
   #   # the result is applicable without changes
   #   return result
   
