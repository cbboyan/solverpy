import subprocess
from .timedsolver import TimedSolver
from .plugins.shell.limits import Limits
from .plugins.shell.timeout import Timeout
from .plugins.shell.memory import Memory
from ..benchmark.path import sids

class ShellSolver(TimedSolver):

   def __init__(self, cmd, limit, builder={}, plugins=[], wait=None, unspace=True):
      self.unspace = unspace
      limits = Limits(limit, builder)
      new = [limits]
      if wait is not None:
         new.append(Timeout(limits.timeout+wait))
      if limits.memory:
         new.append(Memory(limits.memory))
      TimedSolver.__init__(self, limits.timeout, limit=limit, plugins=plugins+new)
      self.cmd = self.decorate(cmd)

   @property
   def name(self):
      return super().name + ":" + self.limit

   def run(self, instance, strategy):
      cmd = self.command(instance, strategy)
      if self.unspace:
         cmd = sids.unspace(cmd)
      try:
         output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as e:
         output = e.output
      return f"### INSTANCE {instance}\n### STRATEGY {strategy}\n### COMMAND: {cmd}\n" + output.decode()

   def command(self, instance, strategy):
      (instance, strategy) = self.translate(instance, strategy)
      return f"{self.cmd} {strategy} {instance}"

