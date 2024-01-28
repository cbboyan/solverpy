from ..decorator import Decorator

TIMEOUT_CMD = "timeout --kill-after=1 --foreground %s"

class Timeout(Decorator):
   
   def __init__(self, timeout):
      self.timeout = timeout
      self.prefix = TIMEOUT_CMD % timeout 
   
   def __repr__(self):
      return f"{type(self).__name__}({repr(self.timeout)})"

   def register(self, solver):
      self.solver = solver
      solver.decorators.insert(0, self)

   def decorate(self, cmd):
      return f"{self.prefix} {cmd}"

   def update(self, instance, strategy, output, result):
      # see man(timeout) for timeout exit codes
      if self.solver.exitcode in [124, 137]:
         result["status"] = "Timeout"

