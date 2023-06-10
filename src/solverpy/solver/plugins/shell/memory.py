from ..decorator import Decorator

ULIMIT_CMD = "ulimit -Sv %d"

class Memory(Decorator):
   
   def __init__(self, giga=4):
      self.prefix = ULIMIT_CMD % int(giga * 1000000)
   
   def decorate(self, cmd):
      return f"{self.prefix} && {cmd}"

   def update(self, instance, strategy, output, result):
      pass

