from typing import Any, TYPE_CHECKING
import re

from ..decorator import Decorator
from ....tools import patterns

if TYPE_CHECKING:
   from ....tools.typing import Result

# real 0.01
# user 0.01
# sys 0.00

TIME_CMD = "/usr/bin/env time -p"

TIME_PAT = re.compile(r"^(real|user|sys) ([0-9.]*)$", re.MULTILINE)

TIME_TABLE = {
   "real": "realtime",
   "user": "usertime",
   "sys": "systime",
}


class Time(Decorator):

   def __init__(self, **kwargs):
      Decorator.__init__(self, **kwargs)
      self.prefix = TIME_CMD

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      del instance, strategy  # unused arguments
      return f"{self.prefix} {cmd}"

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      del instance, strategy  # unused arguments
      res = patterns.keyval(TIME_PAT, output, TIME_TABLE)
      res = patterns.mapval(res, float)
      result.update(res)
      if ("realtime" in res) and ("systime" in res):
         result["runtime"] = res["realtime"] - res["systime"]
         #result["realtime"] = res["realtime"]
         #result["runtime"] = res["usertime"]

