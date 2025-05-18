from typing import Any
import re

from ..decorator import Decorator
from ....tools import patterns

TPTP_STATUS = re.compile(r"^[#%] SZS status (\S*)", re.MULTILINE)

class Tptp(Decorator):

   def __init__(self, **kwargs):
      Decorator.__init__(self, **kwargs)

   def decorate(
      self, 
      cmd : str, 
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
      status = patterns.single(TPTP_STATUS, output, None)
      if status:
         result["status"] = status
      elif "status" not in result:
         result["status"] = "ERROR"

