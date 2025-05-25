from typing import Any, TYPE_CHECKING
import os
import subprocess

from .solverpy import SolverPy
from .plugins.shell.limits import Limits
from .plugins.shell.timeout import Timeout
from .plugins.shell.memory import Memory

if TYPE_CHECKING:
   from .plugins.plugin import Plugin
   from ..tools.typing import LimitBuilder


class StdinSolver(SolverPy):

   def __init__(
      self,
      cmd: str,
      limit: str,
      builder: "LimitBuilder" = {},
      plugins: list["Plugin"] = [],
      wait: (int | None) = None,
      static: str = "", # TODO: rename to `prefix`
      cmdline: bool = False, # set limits using command line arguments?
      inputfile: bool = False,
   ):
      limits = Limits(limit, builder, cmdline=cmdline, inputfile=inputfile)
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
      self._static = static # TODO: rename to `prefix`
      self._cmd = cmd

   @property
   def name(self) -> str:
      return f"{super().name}:{self._limits.limit}"

   def run(self, instance: Any, strategy: Any) -> str:
      inputstr = self.input(instance, strategy)
      env0 = dict(os.environ)
      env0["OMP_NUM_THREADS"] = "1"
      #env0["CUDA_VISIBLE_DEVICES"] = "-1"
      cmd = self.decorate(self._cmd, instance, strategy)
      try:
         output = subprocess.check_output(
            cmd,
            input=inputstr,
            shell=True,
            stderr=subprocess.STDOUT,
            env=env0,
         )
         self._exitcode = 0
      except subprocess.CalledProcessError as e:
         output = e.output
         self._exitcode = e.returncode
      return f"### INSTANCE {instance}\n### STRATEGY {strategy}\n### COMMAND: {cmd}\n" + output.decode()

   def input(self, instance: Any, strategy: Any) -> bytes:
      (instance, strategy) = self.translate(instance, strategy)
      inputstr = self._static.encode()
      inputstr += strategy.encode()
      inputstr += b"\n"
      inputstr += open(instance, "rb").read()
      return inputstr

