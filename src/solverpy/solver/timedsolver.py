import subprocess
from .pluginsolver import PluginSolver

class TimedSolver(PluginSolver):

   def __init__(self, limits, plugins=[]):
      self.limits = limits
      PluginSolver.__init__(self, plugins=plugins+[limits])

   @property
   def name(self):
      return super().name + ":" + str(self.limits)

   @property
   def timeout(self):
      "The set of timeout statuses."
      raise NotImlementedError()
   
