from typing import Any, TYPE_CHECKING

from .solverpy import SolverPy
from .plugins.db.outputs import Outputs

if TYPE_CHECKING:
   from .plugins.plugin import Plugin
   from ..tools.typing import Result


class Reloader(SolverPy):

   def __init__(
      self,
      solver: SolverPy,
      plugins: list["Plugin"] = [],
   ):
      self.solver = solver
      SolverPy.__init__(
         self,
         solver.limits,
         plugins,
      )
      self.outputs = Outputs()
      self.outputs.register(self.solver)

   def run(self, instance: Any, strategy: Any) -> str:
      f = self.outputs.path(instance, strategy)
      with open(f) as fr:
         return fr.read()

   def process(self, output: str) -> "Result":
      return self.solver.process(output)

   def valid(self, result: "Result") -> bool:
      return self.solver.valid(result)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      return self.solver.decorate(cmd, instance, strategy)

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      self.solver.update(instance, strategy, output, result)

   def translate(
      self,
      instance: Any,
      strategy: Any,
   ) -> tuple[Any, Any]:
      return self.solver.translate(instance, strategy)

   @property
   def name(self) -> str:
      return f"{super().name}({self.solver.name})"

   @property
   def success(self) -> frozenset[str]:
      return self.solver.success

   @property
   def timeouts(self) -> frozenset[str]:
      return self.solver.timeouts

