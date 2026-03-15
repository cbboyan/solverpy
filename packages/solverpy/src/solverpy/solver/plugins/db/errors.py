from typing import TYPE_CHECKING

from .outputs import Outputs
from ....benchmark.path import bids

if TYPE_CHECKING:
   from ....tools.typing import Result

NAME = "errors"


class Errors(Outputs):

   def __init__(
      self,
      flatten: bool = True,
      compress: bool = True,
   ):
      Outputs.__init__(self, flatten, compress)
      self._path: str = bids.dbpath(NAME)

   def finished(
      self,
      instance: tuple[str, str],
      strategy: str,
      output: str,
      result: "Result",
   ) -> None:
      if output and not self.solver.valid(result):
         self.write(instance, strategy, output)

