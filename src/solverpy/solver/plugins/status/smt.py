from typing import Any, TYPE_CHECKING
import re

from ..decorator import Decorator
from ....tools import patterns

if TYPE_CHECKING:
   from ....tools.typing import Result

SMT_STATUS = re.compile(r"^(sat|unsat|unknown|timeout)$", re.MULTILINE)


class Smt(Decorator):

   def __init__(self, **kwargs):
      Decorator.__init__(self, **kwargs)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      del instance, strategy # unused arguments
      return cmd

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      del instance, strategy # unused arguments
      status = patterns.single(SMT_STATUS, output, None)
      if status:
         result["status"] = status
      elif "status" not in result:
         result["status"] = "error"

