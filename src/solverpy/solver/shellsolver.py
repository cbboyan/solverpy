import subprocess
from .pluginsolver import PluginSolver
from .plugins.shell.limits import Limits
from .plugins.shell.timeout import Timeout
from ..benchmark.path import sids

class ShellSolver(PluginSolver):

   def __init__(self, cmd, limit, builder={}, plugins=[], wait=None, unspace=True, name=None):
      self.unspace = unspace
      self.limits = Limits(limit, builder)
      new = [ self.limits ]
      if wait is not None:
         new.append(Timeout(self.limits.timeout + wait))
      PluginSolver.__init__(self, plugins=plugins+new, name=name)
      self.cmd = self.decorate(cmd)

   def __str__(self):
      return super().__str__() + ":" + str(self.limits)

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

   def process(self, output):
      raise NotImlementedError()
   
