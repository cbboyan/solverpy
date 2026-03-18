from typing import Any

from ..decorator import Decorator

ULIMIT_CMD = "ulimit -Sv %d"


class Memory(Decorator):
   """Limit virtual memory using `ulimit -Sv` before launching the solver.

   Prepends `ulimit -Sv <kilobytes> &&` to the shell command.  The limit is
   set in kilobytes as `giga * 1024 * 1024 + 1024` to allow a small overhead
   above the nominal gigabyte value.

   Note: `ulimit -Sv` caps *virtual* memory (VSZ), not resident memory (RSS).
   For stricter RSS limits consider a `cgroup`-based approach instead.
   """

   def __init__(self, giga: float = 4):
      """Args:
         giga: Virtual memory limit in gigabytes (default 4 GB).
      """
      Decorator.__init__(self, giga=giga)
      self.prefix = ULIMIT_CMD % (int(giga * 1024 * 1024) + 1024)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      """Prepend `ulimit -Sv <N> &&` to *cmd*."""
      del instance, strategy
      return f"{self.prefix} && {cmd}"
