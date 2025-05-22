from typing import Any, TYPE_CHECKING
import re

from ..decorator import Decorator
from ....tools import patterns

if TYPE_CHECKING:
   from ....tools.typing import Result

TPTP_STATUS = re.compile(r"^[#%] SZS status (\S*)", re.MULTILINE)


class Tptp(Decorator):

   def __init__(self, **kwargs):
      Decorator.__init__(self, **kwargs)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      del instance, strategy
      return cmd

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      del instance, strategy
      status = patterns.single(TPTP_STATUS, output, "")
      if status:
         result["status"] = status
      elif "status" not in result:
         result["status"] = "ERROR"

