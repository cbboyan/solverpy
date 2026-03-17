"""
# Shell-based solver execution

`ShellSolver` runs the solver as a subprocess via the shell.  The solver
binary is invoked as `{cmd} {strategy} {instance}` after all decorator
plugins have had a chance to wrap the command (e.g. prepend `timeout`).
The raw stdout/stderr is returned as a single string and passed to `process`.

Concrete ATP/SMT solvers (E, Vampire, cvc5 …) subclass `ShellSolver` and
only need to supply `_binary`, `process`, and their plugin list.
"""

from typing import Any, TYPE_CHECKING
import os
import shutil
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
   """
   Concrete `SolverPy` that runs the solver binary as a shell subprocess.

   Subclasses set the `_binary` class variable to the default executable name
   and implement `process` to parse the solver output.
   """

   _binary: str = ""
   """Default solver binary name looked up via `shutil.which`."""

   @classmethod
   def available(cls) -> bool:
      """Return `True` if the default solver binary is found in `PATH`."""
      return shutil.which(cls._binary) is not None

   def isinstalled(self) -> bool:
      """Return `True` if this instance's binary is found in `PATH`."""
      return shutil.which(self._binary) is not None

   def __init__(
      self,
      cmd: str,
      limit: str,
      builder: "LimitBuilder" = {},
      plugins: list["Plugin"] = [],
      wait: (int | None) = None,
      unspace: bool = True,
      binary: str = "",
   ):
      """
      Args:
          cmd: base shell command for the solver (e.g. `/usr/bin/eprover`).
          limit: resource limit string (e.g. `"T10"` for 10-second timeout).
          builder: mapping used to derive additional limit flags from the limit string.
          plugins: extra plugins registered before the built-in limit plugins.
          wait: extra seconds added to the wall-clock `timeout` wrapper on top
              of the solver's own time limit, giving it time to shut down cleanly.
          unspace: if `True`, replace spaces in the command with `%20` via
              `sids.unspace` before passing to the shell.
          binary: override the default `_binary` for this instance.
      """
      self._unspace = unspace
      self._binary = binary
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
      """Solver name including the resource limit, e.g. `E:T10`."""
      return f"{super().name}:{self._limits.limit}"

   def run(self, instance: Any, strategy: Any) -> str:
      """
      Build the shell command and run it, returning combined stdout/stderr.

      The output is prefixed with header lines recording the instance, strategy,
      and full command for later parsing by `process`.
      """
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
      """
      Build the full shell command string: decorate the base command, translate
      instance/strategy, then assemble as `{cmd} {strategy} {instance}`.
      """
      cmd = self.decorate(self._cmd, instance, strategy)
      (instance, strategy) = self.translate(instance, strategy)
      return f"{cmd} {strategy} {instance}"

