import subprocess
from .timedsolver import TimedSolver
from .plugins.shell.limits import Limits
from .plugins.shell.timeout import Timeout
from ..benchmark.path import sids

class ShellSolver(TimedSolver):

   def __init__(self, cmd, limit, builder={}, plugins=[], wait=None, unspace=True):
      self.unspace = unspace
      limits = Limits(limit, builder)
      if wait is not None:
         plugins = plugins + [Timeout(limits.timeout+wait)]
      TimedSolver.__init__(self, limits, plugins=plugins)
      self.cmd = self.decorate(cmd)

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

