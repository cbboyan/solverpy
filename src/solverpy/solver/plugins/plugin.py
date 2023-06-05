
class Plugin:

   def __repr__(self):
      return f"{type(self).__name__}()"

   def register(self, solver):
      raise NotImlementedError()

