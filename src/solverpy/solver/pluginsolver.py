import logging
from .solver import Solver

logger = logging.getLogger(__name__)
  
class PluginSolver(Solver):

   def __init__(self, plugins=[], name=None):
      Solver.__init__(self, name=name)
      self.decorators = []
      self.translators = []
      self.init(plugins)

   def solve(self, instance, strategy):
      (output, result) = super().solve(instance, strategy)
      self.update(instance, strategy, output, result)
      if not self.valid(result):
         lines = output.split("\n")
         if len(lines) > 3:
            msg = f"{lines[2]}\n{lines[3]}" # command and first output line
         else:
            msg = output
         logger.debug(f"failed solver run: {self}:{strategy} @ {instance}\n{msg}")
      return result
   
   # plugins initization
   def init(self, plugins):
      for plugin in plugins:
         plugin.register(self)
   
   # decorators
   def decorate(self, cmd):
      for plugin in self.decorators:
         cmd = plugin.decorate(cmd)
      return cmd
   
   def update(self, instance, strategy, output, result):
      for plugin in self.decorators:
         plugin.update(instance, strategy, output, result)
      for plugin in self.decorators:
         plugin.finished(instance, strategy, output, result)

   # translators
   def translate(self, instance, strategy):
      for plugin in self.translators:
         (instance, strategy) = plugin.translate(instance, strategy)
      return (instance, strategy)

