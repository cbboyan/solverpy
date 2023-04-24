import re

from ..decorator import Decorator
from ....tools import patterns

SMT_STATUS = re.compile(r"^(sat|unsat|unknown|timeout)$", re.MULTILINE)

class Smt(Decorator):

   def __init__(self):
      pass

   def decorate(self, cmd):
      return cmd

   def update(self, instance, strategy, output, result):
      result["status"] = patterns.single(SMT_STATUS, output, "error")

