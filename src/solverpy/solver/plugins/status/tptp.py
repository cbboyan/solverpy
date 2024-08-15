import re

from ..decorator import Decorator
from ....tools import patterns

TPTP_STATUS = re.compile(r"^[#%] SZS status (\S*)", re.MULTILINE)

class Tptp(Decorator):

   def __init__(self):
      pass

   def decorate(self, cmd, instance, strategy):
      return cmd

   def update(self, instance, strategy, output, result):
      status = patterns.single(TPTP_STATUS, output, None)
      if status:
         result["status"] = status
      elif "status" not in result:
         result["status"] = "ERROR"

