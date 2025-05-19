from typing import Any

from ..decorator import Decorator

ULIMIT_CMD = "ulimit -Sv %d"


class Memory(Decorator):

   def __init__(self, giga: int = 4):
      Decorator.__init__(self, giga=giga)
      self.prefix = ULIMIT_CMD % int(giga * 1000000)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      del instance, strategy
      return f"{self.prefix} && {cmd}"

