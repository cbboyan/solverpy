from typing import Any
import re

from ..decorator import Decorator
from ....tools import patterns

SMT_STATUS = re.compile(r"^(sat|unsat|unknown|timeout)$", re.MULTILINE)

class Smt(Decorator):

   def __init__(self, **kwargs):
      Decorator.__init__(self, **kwargs)

   def decorate(
      self, 
      cmd: str, 
      instance: Any, 
      strategy: Any
   ) -> str:
      return cmd

   def update(
      self, 
      instance: Any, 
      strategy: Any, 
      output: str, 
      result: dict
   ) -> None:
      status = patterns.single(SMT_STATUS, output, None)
      if status:
         result["status"] = status
      elif "status" not in result:
         result["status"] = "error"

