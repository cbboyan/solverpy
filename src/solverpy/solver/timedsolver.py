import subprocess
from .pluginsolver import PluginSolver
from .plugins.status.timeouter import Timeouter

class TimedSolver(PluginSolver):

   def __init__(self, timeout, limit=None, plugins=[]):
      self.timeout = timeout
      self.limit = limit if limit else f"T{timeout}"
      #assert(self.limit.startswith("T"))
      new = [Timeouter()]
      PluginSolver.__init__(self, plugins=plugins+new)

   def __repr__(self):
      plgs = super().__repr__()
      plgs = f", plugins=[{plgs}]" if plgs else ""
      return f"{type(self).__name__}('{self.limit}'{plgs})"

   @property
   def timeouts(self):
      "The set of timeout statuses."
      raise NotImlementedError()

   def simulate(self, result):
      "Simulate run from the past result."
      if "timeout" in result:
         # the cached result is timeout
         if result["runtime"] < self.timeout:
            # recompute since we have more time
            return None
      else:
         # the cached result is solved
         if result["runtime"] > self.timeout:
            # simulated timeout
            return dict(result, 
                        status="TIMEOUT", 
                        runtime=self.timeout)
      # the result is applicable without changes
      return result
   
