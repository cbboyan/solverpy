import re

from ..decorator import Decorator
from ....tools import patterns

TPTP_STATUS = re.compile(r"^[#%] SZS status (\S*)", re.MULTILINE)

class Tptp(Decorator):

   def __init__(self):
      pass

   def decorate(self, cmd):
      return cmd

   def update(self, instance, strategy, output, result):
      result["status"] = patterns.single(TPTP_STATUS, output, "Error")

