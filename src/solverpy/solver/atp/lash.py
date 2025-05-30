from typing import TYPE_CHECKING
import re

from ..shellsolver import ShellSolver
from ...tools import patterns, human
from ..plugins.status.tptp import Tptp
from ..plugins.shell.time import Time

if TYPE_CHECKING:
   from ..plugins.plugin import Plugin
   from ...tools.typing import LimitBuilder

L_BINARY = "lash"

#L_STATIC = "-p tstp -m mode0 -M %s" % getenv("LASH_MODE_DIR", "./modes")
L_STATIC = "-p tstp"

L_PAT = re.compile(r"^% (Steps|Mode): (\S*)$", flags=re.MULTILINE)

L_BUILDER: "LimitBuilder" = {
   "T": "",
}

L_TABLE = {
   "Steps": "Steps",
   "Mode": "Mode",
}


class Lash(ShellSolver):

   def __init__(
      self,
      limit: str,
      binary: str = L_BINARY,
      static: str = L_STATIC,
      complete: bool = True,
      plugins: list["Plugin"] = [],
   ):
      cmd = f"{binary} {static}"
      plugins = plugins + [
         Time(),
         Tptp(complete=complete),
      ]
      ShellSolver.__init__(
         self,
         cmd,
         limit,
         L_BUILDER,
         plugins,
         0,
         complete,
      )

   def process(self, output):
      result = patterns.keyval(L_PAT, output, L_TABLE)
      result = patterns.mapval(result, human.numeric)
      return result

