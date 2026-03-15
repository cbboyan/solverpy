"""
# Solver extension plugins

The class [`PluginSolver`][solverpy.solver.pluginsolver.PluginSolver] extends
[`Solver`][solverpy.solver.solver.Solver] to add support for plugins. 
[`Plugin`][solverpy.solver.plugins.plugin.Plugin]'s can extend or modify the
behavior of the solver. There are two types of plugins: _decorators_ and
_translators_. 

* [`Decorator`][solverpy.solver.plugins.decorator]'s are used to modify the
command and the output result of the solver. Typically decorators are used to
add timing information to the solver output, and parse standardized solver
output, like TPTP or SMT2. 
* [`Translator`][solverpy.solver.plugins.translator]'s are used to translate
the instance and strategy for the
[`Solver.solve`][solverpy.solver.solver.Solver.solve] method, for example,
translating a benchmark-problem pair to a filename.

A single solver can register multiple plugins.
The order of registration might matter.
The basic abstract class for plugins is [`Plugin`][solverpy.solver.plugins.plugin.Plugin].

```plantuml name="solver-plugins"

abstract class solverpy.solver.pluginsolver.PluginSolver {
   # decorators : list[Decorator]
   # translators : list[Translator]
   --
   + solve(instance, strategy) : Result
}

abstract class solverpy.solver.plugins.plugin.Plugin {
   + register(solver)
}

abstract class solverpy.solver.plugins.decorator.Decorator extends solverpy.solver.plugins.plugin.Plugin 

abstract class solverpy.solver.plugins.translator.Translator extends solverpy.solver.plugins.plugin.Plugin 

solverpy.solver.plugins.plugin.Plugin "*" o-r- solverpy.solver.pluginsolver.PluginSolver

```

For more on plugins, check the [`plugins`][solverpy.solver.plugins] module. The
direct superclass of
[`PluginSolver`][solverpy.solver.pluginsolver.PluginSolver] 
is [`SolverPy`][solverpy.solver.solverpy.SolverPy] which adds database support.
"""

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
   """
   ```plantuml name="solver-pluginsolver"
   abstract class solverpy.solver.solver.Solver
   abstract class solverpy.solver.pluginsolver.PluginSolver extends solverpy.solver.solver.Solver {
      # decorators : list[Decorator]
      # translators : list[Translator]
      + init(plugins) 
      + decorate(cmd, instance, strategy) : str
      + translate(instance, strategy) : tuple
      + update(instance, strategy, output, result) 
      + call(pid, method, arguments)
   }
   abstract class solverpy.solver.solverpy.SolverPy extends solverpy.solver.pluginsolver.PluginSolver
   ```
   """

   def __init__(self, plugins: list["Plugin"] = [], **kwargs: Any):
      Solver.__init__(self, **kwargs)
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
      """
      Run the solver with the strategy on the instatance. Update the 
      solver result and announce the final version. Return the updated
      result.
      """
      result = Solver.solve(self, instance, strategy)
      output = self._output
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

   def init(self, plugins: list["Plugin"]) -> None:
      """Plugins initialization."""
      for plugin in plugins:
         plugin.register(self)

   def decorate(
      self,
      cmd: str,
      instance: Any,
      strategy: Any,
   ) -> str:
      """Decorate the command for the solver."""
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
      """Update the solver result and announce the final version."""
      for plugin in self.decorators:
         plugin.update(instance, strategy, output, result)
      for plugin in self.decorators:
         plugin.finished(instance, strategy, output, result)

   def translate(
      self,
      instance: Any,
      strategy: Any,
   ) -> tuple[Any, Any]:
      """Translate the instance and strategy for the solver."""
      for plugin in self.translators:
         (instance, strategy) = plugin.translate(instance, strategy)
      return (instance, strategy)

   def call(
      self,
      pid: str,
      method: str,
      *args,
      **kwargs,
   ):
      """Call `method` of the plugin(s) `pid`.""" 
      for plugin in self.translators + self.decorators:
         if (plugin.id == pid):
            if hasattr(plugin, method):
               handler = getattr(plugin, method)
               handler(*args, **kwargs)
            else:
               logger.warning(f"Unknown method {method} of plugin {pid}")
