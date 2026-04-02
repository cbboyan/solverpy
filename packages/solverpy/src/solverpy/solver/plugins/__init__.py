"""
# Plugins

Plugins are lightweight extensions that modify how a solver processes its inputs
and outputs without requiring subclassing.  They are attached to a
[`PluginSolver`][solverpy.solver.pluginsolver.PluginSolver] at construction time
and called at fixed points in the solve lifecycle.

```plantuml name="solver-plugins"
abstract class solverpy.solver.pluginsolver.PluginSolver {
   + decorators : list[Decorator]
   + translators : list[Translator]
   --
   + init(plugins)
   + call(pid, method)
}

abstract class solverpy.solver.plugins.plugin.Plugin {
   # _id : str
   # _enabled : bool
   --
   + register(solver)
   + enable()
   + disable()
}

abstract class solverpy.solver.plugins.decorator.Decorator extends solverpy.solver.plugins.plugin.Plugin {
   + decorate(cmd, instance, strategy) : str
   + update(instance, strategy, output, result)
   + finished(instance, strategy, output, result)
}

abstract class solverpy.solver.plugins.translator.Translator extends solverpy.solver.plugins.plugin.Plugin {
   + translate(instance, strategy) : tuple
}

solverpy.solver.pluginsolver.PluginSolver "1" o-right "n" solverpy.solver.plugins.plugin.Plugin

class solverpy.solver.plugins.shell.Limits extends solverpy.solver.plugins.decorator.Decorator
solverpy.solver.plugins.shell.Limits --|> solverpy.solver.plugins.translator.Translator
class solverpy.solver.plugins.shell.Timeout extends solverpy.solver.plugins.decorator.Decorator
class solverpy.solver.plugins.shell.Time extends solverpy.solver.plugins.decorator.Decorator
class solverpy.solver.plugins.shell.Memory extends solverpy.solver.plugins.decorator.Decorator

class solverpy.solver.plugins.status.Tptp extends solverpy.solver.plugins.decorator.Decorator
class solverpy.solver.plugins.status.Smt extends solverpy.solver.plugins.decorator.Decorator
class solverpy.solver.plugins.status.Limiter extends solverpy.solver.plugins.decorator.Decorator

class solverpy.solver.plugins.db.Bid extends solverpy.solver.plugins.translator.Translator
class solverpy.solver.plugins.db.Sid extends solverpy.solver.plugins.translator.Translator
class solverpy.solver.plugins.db.Outputs extends solverpy.solver.plugins.decorator.Decorator
class solverpy.solver.plugins.db.Errors extends solverpy.solver.plugins.db.Outputs
```

## Plugin roles

Two abstract base classes define the two roles a plugin can play:

| Role | Base class | Called during |
|---|---|---|
| [`Decorator`][solverpy.solver.plugins.decorator.Decorator] | wraps the shell command; post-processes the solver output |
| [`Translator`][solverpy.solver.plugins.translator.Translator] | transforms `(instance, strategy)` inputs before the solver runs |

## Solve lifecycle

Each call to `solver.solve(instance, strategy)` follows these steps:

1. All **translators** transform `(instance, strategy)` in registration order.
2. The solver builds its shell command and each **decorator** wraps it via `decorate()`.
3. The subprocess runs.
4. Each decorator's `update()` is called to extract data from the raw output.
5. Each decorator's `finished()` is called for any post-update side-effects (e.g. writing files).

## Connecting plugins to a solver

Pass plugins as a list to the solver constructor; `init()` registers each one:

```python
from solverpy.solver.plugins import db
solver = E("T10", plugins=db())     # Bid and Sid are registered
```

To call a method on a specific plugin by id, use `solver.call()`:

```python
solver.call("trains", "disable")    # disable training data collection
```

## Standalone DB access

[`Bid`][solverpy.solver.plugins.db.bid.Bid] and
[`Sid`][solverpy.solver.plugins.db.sid.Sid] can be used outside a solver to
resolve identifiers independently:

```python
from solverpy.benchmark.path import bids, sids
path    = bids.path(bid, problem)   # (bid, problem) -> file path
options = sids.load(sid)            # sid -> strategy string
```

[`Outputs`][solverpy.solver.plugins.db.outputs.Outputs] and
[`Errors`][solverpy.solver.plugins.db.errors.Errors] write directly to the
`solverpy_db/outputs/` and `solverpy_db/errors/` directories and can be
instantiated standalone to inspect or write cached output files.

## Submodules

| Submodule | Plugins | Purpose |
|---|---|---|
| [`shell`][solverpy.solver.plugins.shell] | Limits, Timeout, Time, Memory | subprocess launch control and resource limits |
| [`status`][solverpy.solver.plugins.status] | Tptp, Smt, Limiter | solver output parsing; result status population |
| [`db`][solverpy.solver.plugins.db] | Bid, Sid, Outputs, Errors | benchmark database bridge |

"""

from .db.bid import Bid
from .db.sid import Sid
from .db.eprovesid import EProverSid
from .db.outputs import Outputs
from .db.errors import Errors

def db():
   """Return the standard set of DB plugins: `[Bid(), Sid()]`.

   These two translators are required for benchmark evaluation — `Bid`
   resolves the `(bid, problem)` instance pair to a file path and `Sid`
   loads the strategy definition from `solverpy_db/strats/`.
   """
   return [
      Bid(),
      Sid(),
   ]

def outputs(flatten=True, compress=True):
   """Return DB plugins plus output-capture plugins for debugging.

   Returns `[Bid(), Sid(), Outputs(...), Errors(...)]`.  Solver stdout is
   written to `solverpy_db/outputs/` for successful runs and to
   `solverpy_db/errors/` for failed or incomplete runs.

   Args:
      flatten: Replace `/` in problem paths with `_._` to avoid nested
         directories in the output tree.
      compress: Gzip-compress the written output files.
   """
   return [
      Bid(),
      Sid(),
      Outputs(flatten, compress),
      Errors(flatten, compress),
   ]

__all__ = ["db", "outputs"]

