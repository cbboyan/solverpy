"""
# Status plugins

Status plugins parse the raw solver output and populate the `status` key of
the result.  They also register the solver's valid, successful and timeout
statuses so that [`valid`][solverpy.solver.solver.Solver.valid] and
[`solved`][solverpy.solver.solver.Solver.solved] work correctly.

```plantuml name="solver-plugins-status"

abstract class solverpy.solver.plugins.decorator.Decorator

class solverpy.solver.plugins.status.tptp.Tptp extends solverpy.solver.plugins.decorator.Decorator
class solverpy.solver.plugins.status.smt.Smt extends solverpy.solver.plugins.decorator.Decorator
class solverpy.solver.plugins.status.limiter.Limiter extends solverpy.solver.plugins.decorator.Decorator

```

| Plugin | Used by | Description |
|---|---|---|
| [`Tptp`][solverpy.solver.plugins.status.tptp.Tptp] | E, Vampire, Lash, Prover9 | Parses TPTP SZS status line from solver output |
| [`Smt`][solverpy.solver.plugins.status.smt.Smt] | Cvc5, Z3, Bitwuzla | Parses SMT-LIB2 status (`sat`/`unsat`/`unknown`) |
| [`Limiter`][solverpy.solver.plugins.status.limiter.Limiter] | optional | Caps `runtime` at the time limit; adds `limit` key to result |

"""

from .smt import Smt
from .tptp import Tptp
from .limiter import Limiter

__all__ = ["Smt", "Tptp", "Limiter"]

