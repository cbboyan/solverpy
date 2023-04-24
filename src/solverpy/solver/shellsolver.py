import subprocess
from .timedsolver import TimedSolver
from .plugins.shell.limits import Limits
from .plugins.shell.timeout import Timeout

class ShellSolver(TimedSolver):

   def __init__(self, cmd, limit, builder={}, plugins=[], wait=None):
      self.limits = Limits(limit, builder)
      new = [ self.limits ]
      if wait is not None:
         new.append(Timeout(self.limits.timeout + wait))
      TimedSolver.__init__(self, self.limits.timeout, plugins + new)
      self.cmd = self.decorate(cmd)

   def run(self, instance, strategy):
      cmd = self.command(instance, strategy)
      try:
         output = subprocess.check_output(cmd, shell=True, 
            stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as e:
         output = e.output
      return f"### COMMAND: {cmd}\n" + output.decode()

   def command(self, instance, strategy):
      (instance, strategy) = self.translate(instance, strategy)
      return f"{self.cmd} {strategy} {instance}"

   def process(self, output):
      raise NotImlementedError()
   
