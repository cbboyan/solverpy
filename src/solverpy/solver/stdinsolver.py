import os
import subprocess
from .timedsolver import TimedSolver
from .plugins.shell.limits import Limits
from .plugins.shell.timeout import Timeout
from .plugins.shell.memory import Memory

class StdinSolver(TimedSolver):

   def __init__(self, cmd, limit, builder={}, plugins=[], wait=None, static=""):
      limits = Limits(limit, builder, cmdline=False)
      new = [limits]
      if wait is not None:
         new.append(Timeout(limits.timeout+wait))
      if limits.memory:
         new.append(Memory(limits.memory))
      TimedSolver.__init__(self, limits.timeout, limits=limits, plugins=plugins+new)
      self.static = static
      self.cmd = self.decorate(cmd)

   @property
   def name(self):
      return f"{super().name}:{self.limits.limit}"

   def run(self, instance, strategy):
      inputstr = self.input(instance, strategy)
      env0 = dict(os.environ)
      env0["OMP_NUM_THREADS"] = "1"
      #env0["CUDA_VISIBLE_DEVICES"] = "-1"
      try:
         output = subprocess.check_output(self.cmd, input=inputstr, 
            shell=True, stderr=subprocess.STDOUT, env=env0)
      except subprocess.CalledProcessError as e:
         output = e.output
      return f"### INSTANCE {instance}\n### STRATEGY {strategy}\n### COMMAND: {self.cmd}\n" + output.decode()

   def input(self, instance, strategy):
      (instance, strategy) = self.translate(instance, strategy)
      inputstr = self.static.encode()
      inputstr += strategy.encode()
      inputstr += b"\n"
      inputstr += open(instance, "rb").read()
      print("cmd", self.cmd)
      return inputstr

