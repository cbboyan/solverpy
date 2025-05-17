from ..decorator import Decorator

TIMEOUT_CMD = "timeout --kill-after=15 --foreground %s"

class Timeout(Decorator):
   
   def __init__(self, timeout):
      Decorator.__init__(self, timeout=timeout)
      self.timeout = timeout
      self.prefix = TIMEOUT_CMD % timeout 
   
   def register(self, solver):
      self.solver = solver
      solver.decorators.insert(0, self)

   def decorate(self, cmd, instance, strategy):
      return f"{self.prefix} {cmd}"

   def update(self, instance, strategy, output, result):
      # see man(timeout) for timeout exit codes
      if self.solver.exitcode in [124, 137]:
         result["status"] = "TIMEOUT"

