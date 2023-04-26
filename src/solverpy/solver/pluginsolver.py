from .solver import Solver
  
class PluginSolver(Solver):

   def __init__(self, plugins=[]):
      self.providers = []
      self.decorators = []
      self.translators = []
      self.init(plugins)

   def solve(self, instance, strategy):
      result = self.query(instance, strategy)
      if not result: 
         (output, result) = super().solve(instance, strategy)
         self.update(instance, strategy, output, result)
         self.store(instance, strategy, output, result)
      else:
         self.store(instance, strategy, None, result)
      return result
   
   def applicable(self, result):
      return self.solved(result)
   
   # plugins initization
   def init(self, plugins):
      for plugin in plugins:
         plugin.register(self)
   
   # providers
   def query(self, instance, strategy):
      for plugin in self.providers:
         result = plugin.query(instance, strategy)
         if result and self.applicable(result):
            return result
      return None

   def store(self, instance, strategy, output, result):
      for plugin in self.providers:
         plugin.store(instance, strategy, output, result)
   
   def flush(self):
      for plugin in self.providers:
         plugin.flush()

   # decorators
   def decorate(self, cmd):
      for plugin in self.decorators:
         cmd = plugin.decorate(cmd)
      return cmd
   
   def update(self, instance, strategy, output, result):
      for plugin in self.decorators:
         plugin.update(instance, strategy, output, result)

   # translators
   def translate(self, instance, strategy):
      for plugin in self.translators:
         (instance, strategy) = plugin.translate(instance, strategy)
      return (instance, strategy)

