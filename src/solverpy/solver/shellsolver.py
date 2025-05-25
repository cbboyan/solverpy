from typing import Any, TYPE_CHECKING
import os
import subprocess

from .solverpy import SolverPy
from .plugins.shell.limits import Limits
from .plugins.shell.timeout import Timeout
from .plugins.shell.memory import Memory
from ..benchmark.path import sids

if TYPE_CHECKING:
   from .plugins.plugin import Plugin
   from ..tools.typing import LimitBuilder


class ShellSolver(SolverPy):

   def __init__(
      self,
      cmd: str,
      limit: str,
      builder: "LimitBuilder" = {},
      plugins: list["Plugin"] = [],
      wait: (int | None) = None,
      unspace: bool = True,
   ):
      self._unspace = unspace
      limits = Limits(limit, builder)
      new: list["Plugin"] = [limits]
      if wait is not None:
         new.append(Timeout(limits.timeout + wait))
      if limits.memory:
         new.append(Memory(limits.memory))
      SolverPy.__init__(
         self,
         limits=limits,
         plugins=plugins + new,
      )
      self._cmd = cmd

   @property
   def name(self) -> str:
      return f"{super().name}:{self._limits.limit}"

   def run(self, instance: Any, strategy: Any) -> str:
      cmd = self.command(instance, strategy)
      env0 = dict(os.environ)
      env0["OMP_NUM_THREADS"] = "1"
      #env0["CUDA_VISIBLE_DEVICES"] = "-1"
      if self._unspace:
         cmd = sids.unspace(cmd)
      self._exitcode = 0
      try:
         output = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            env=env0,
         )
      except subprocess.CalledProcessError as e:
         output = e.output
         self._exitcode = e.returncode
      return f"### INSTANCE {instance}\n### STRATEGY {strategy}\n### COMMAND: {cmd}\n" + output.decode()

   def command(self, instance: Any, strategy: Any) -> str:
      cmd = self.decorate(self._cmd, instance, strategy)
      (instance, strategy) = self.translate(instance, strategy)
      return f"{cmd} {strategy} {instance}"

