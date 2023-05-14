from .plugin import Plugin

class Decorator(Plugin):

   def register(self, solver):
      solver.decorators.append(self)
   
   def decorate(self, cmd):
      return cmd

   def update(self, instance, strategy, output, result):
      return 

   def finished(self, instance, strategy, output, result):
      return

