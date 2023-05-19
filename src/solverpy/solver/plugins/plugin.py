
class Plugin:

   def __repr__(self):
      return type(self).__name__

   def register(self, solver):
      raise NotImlementedError()

