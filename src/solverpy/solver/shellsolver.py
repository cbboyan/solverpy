import os
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
      TimedSolver.__init__(self, limits.timeout, limits=limits, plugins=plugins+new)
      self.cmd = self.decorate(cmd)

   @property
   def name(self):
      return f"{super().name}:{self.limits.limit}"

   def run(self, instance, strategy):
      cmd = self.command(instance, strategy)
      env0 = dict(os.environ)
      env0["OMP_NUM_THREADS"] = "1"
      #env0["CUDA_VISIBLE_DEVICES"] = "-1"
      if self.unspace:
         cmd = sids.unspace(cmd)
      self.exitcode = 0
      try:
         output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, env=env0)
      except subprocess.CalledProcessError as e:
         output = e.output
         self.exitcode = e.returncode
      return f"### INSTANCE {instance}\n### STRATEGY {strategy}\n### COMMAND: {cmd}\n" + output.decode()

   def command(self, instance, strategy):
      (instance, strategy) = self.translate(instance, strategy)
      return f"{self.cmd} {strategy} {instance}"

