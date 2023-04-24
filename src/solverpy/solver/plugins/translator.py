from .plugin import Plugin

class Translator(Plugin):

   def register(self, solver):
      solver.translators.append(self)

   def translate(self, instance, strategy):
      return (instance, strategy)
