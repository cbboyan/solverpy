import re

from ..decorator import Decorator
from ....tools import patterns

# real 0.01
# user 0.01
# sys 0.00

TIME_CMD = "/usr/bin/env time -p"

TIME_PAT = re.compile(r"^(real|user|sys) ([0-9.]*)$", re.MULTILINE)

TIME_TABLE = {
   "real": "realtime",
   "user": "usertime",
   "sys" : "systime",
}

class Time(Decorator):

   def __init__(self):
      self.prefix = TIME_CMD

   def decorate(self, cmd):
      return f"{self.prefix} {cmd}"

   def update(self, instance, strategy, output, result):
      res = patterns.keyval(TIME_PAT, output, TIME_TABLE)
      res = patterns.mapval(res, float)
      result.update(res)
      if ("realtime" in res) and ("systime" in res):
         result["runtime"] = res["realtime"] - res["systime"]
         #result["realtime"] = res["realtime"]
         #result["runtime"] = res["usertime"] 

