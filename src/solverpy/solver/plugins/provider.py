from .plugin import Plugin

class Provider(Plugin):

   def register(self, solver):
      solver.providers.append(self)

   def query(self, instance, strategy):
      return None

   def store(self, instance, strategy, output, result):
      pass

