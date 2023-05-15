import subprocess
from .pluginsolver import PluginSolver

class TimedSolver(PluginSolver):

   def __init__(self, timelimit, limitname=None, plugins=[]):
      self.timelimit = timelimit
      self.limitname = limitname if limitname else f"T{timelimit}"
      PluginSolver.__init__(self, plugins=plugins)

   @property
   def timeouts(self):
      "The set of timeout statuses."
      raise NotImlementedError()
   
