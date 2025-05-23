from typing import Any

from ..decorator import Decorator

ULIMIT_CMD = "ulimit -Sv %d"


class Memory(Decorator):

   def __init__(self, giga: float = 4):
      Decorator.__init__(self, giga=giga)
      self.prefix = ULIMIT_CMD % int(giga * 1024 * 1024)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      del instance, strategy
      return f"{self.prefix} && {cmd}"
