from typing import Any, TYPE_CHECKING
import logging

from .solver import Solver

if TYPE_CHECKING:
   from .plugins.plugin import Plugin
   from .plugins.decorator import Decorator
   from .plugins.translator import Translator
   from ..tools.typing import Result

logger = logging.getLogger(__name__)


class PluginSolver(Solver):

   def __init__(self, plugins: list["Plugin"] = []):
      self.decorators: list["Decorator"] = []
      self.translators: list["Translator"] = []
      self.init(plugins)

   def represent(self):
      return dict(
         cls=self.name,
         decorators=[repr(x) for x in self.decorators],
         translators=[repr(x) for x in self.translators],
      )

   def solve(self, instance: Any, strategy: Any) -> "Result":
      (output, result) = super().solve(instance, strategy)
      self.update(instance, strategy, output, result)
      if not self.valid(result):
         lines = output.split("\n")
         if len(lines) > 3:
            msg = f"{lines[2]}\n{lines[3]}"  # command and first output line
         else:
            msg = output
         logger.debug(
            f"failed solver run: {self}:{strategy} @ {instance}\nresult: {result}\n{msg}"
         )
      return result

   # plugins initization
   def init(self, plugins: list["Plugin"]) -> None:
      for plugin in plugins:
         plugin.register(self)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      for plugin in self.decorators:
         cmd = plugin.decorate(cmd, instance, strategy)
      return cmd

   def update(
      self,
      instance: Any,
      strategy: Any,
      output: str,
      result: "Result",
   ) -> None:
      for plugin in self.decorators:
         plugin.update(instance, strategy, output, result)
      for plugin in self.decorators:
         plugin.finished(instance, strategy, output, result)

   def translate(
      self,
      instance: Any,
      strategy: Any,
   ) -> tuple[Any, Any]:
      for plugin in self.translators:
         (instance, strategy) = plugin.translate(instance, strategy)
      return (instance, strategy)

