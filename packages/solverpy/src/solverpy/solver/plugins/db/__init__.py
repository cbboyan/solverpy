"""
# DB plugins

DB plugins bridge the solver and the benchmark database.  They translate
abstract identifiers — benchmark ids and strategy ids — into concrete inputs
for the solver, and write solver outputs back to the database.

```plantuml name="solver-plugins-db"

abstract class solverpy.solver.plugins.translator.Translator
abstract class solverpy.solver.plugins.decorator.Decorator

class solverpy.solver.plugins.db.bid.Bid extends solverpy.solver.plugins.translator.Translator
class solverpy.solver.plugins.db.sid.Sid extends solverpy.solver.plugins.translator.Translator
class solverpy.solver.plugins.db.outputs.Outputs extends solverpy.solver.plugins.decorator.Decorator
class solverpy.solver.plugins.db.errors.Errors extends solverpy.solver.plugins.db.outputs.Outputs

```

| Plugin | Description |
|---|---|
| [`Bid`][solverpy.solver.plugins.db.bid.Bid] | Translates a `(bid, problem)` instance pair to the full problem file path |
| [`Sid`][solverpy.solver.plugins.db.sid.Sid] | Loads a strategy definition from `solverpy_db/strats/` by strategy id; handles parametric strategies |
| [`Outputs`][solverpy.solver.plugins.db.outputs.Outputs] | Writes raw solver output to `solverpy_db/outputs/` for successful runs |
| [`Errors`][solverpy.solver.plugins.db.errors.Errors] | Writes raw solver output to `solverpy_db/errors/` for failed/incomplete runs |

"""

from .bid import Bid
from .sid import Sid
from .eprovesid import EProverSid

__all__ = ["Bid", "Sid", "EProverSid"]

