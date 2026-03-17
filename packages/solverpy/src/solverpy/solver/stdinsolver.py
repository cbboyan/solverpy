"""
# Stdin-based solver execution

`StdinSolver` runs the solver binary as a subprocess and feeds the problem
to it via **stdin** rather than as a command-line filename argument.  This is
used for solvers like cvc5 that accept SMT-LIB input on stdin.

The input stream is assembled as: `static_prefix + strategy_options + newline
+ problem_file_contents`.  Resource limits are applied identically to
`ShellSolver` via the `Limits` / `Timeout` / `Memory` plugin chain.
"""

from typing import Any, TYPE_CHECKING
import os
import shutil
import subprocess

from .solverpy import SolverPy
from .plugins.shell.limits import Limits
from .plugins.shell.timeout import Timeout
from .plugins.shell.memory import Memory

if TYPE_CHECKING:
   from .plugins.plugin import Plugin
   from ..tools.typing import LimitBuilder


class StdinSolver(SolverPy):
   """
   Concrete `SolverPy` that pipes problem input to the solver via stdin.

   Used for solvers that read SMT-LIB (or similar) input from stdin rather
   than accepting a filename on the command line.
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
      static: str = "", # TODO: rename to `prefix`
      cmdline: bool = False, # set limits using command line arguments?
      inputfile: bool = False,
      binary: str = "",
   ):
      """
      Args:
          cmd: base shell command for the solver (e.g. `cvc5`).
          limit: resource limit string (e.g. `"T10"`).
          builder: mapping used to derive additional limit flags.
          plugins: extra plugins registered before the built-in limit plugins.
          wait: extra wall-clock seconds added on top of the solver time limit.
          static: fixed prefix prepended to every stdin payload (e.g. solver options).
          cmdline: if `True`, pass limits as command-line arguments instead of
              relying on the `timeout` wrapper.
          inputfile: if `True`, write stdin to a temp file and pass the path
              instead (for solvers that require a file argument even in stdin mode).
          binary: override the default `_binary` for this instance.
      """
      self._binary = binary
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
      """Solver name including the resource limit, e.g. `Cvc5:T10`."""
      return f"{super().name}:{self._limits.limit}"

   def run(self, instance: Any, strategy: Any) -> str:
      """
      Build the stdin payload, run the solver, and return combined stdout/stderr.

      The output is prefixed with header lines recording the instance, strategy,
      and full command for later parsing by `process`.
      """
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
      """
      Assemble the stdin bytes: `static + strategy + newline + problem_file_contents`.
      Translators are applied to `(instance, strategy)` before assembly.
      """
      (instance, strategy) = self.translate(instance, strategy)
      inputstr = self._static.encode()
      inputstr += strategy.encode()
      inputstr += b"\n"
      inputstr += open(instance, "rb").read()
      #open(f"/home/yan/tmp.smt2", "wb").write(inputstr)
      return inputstr

