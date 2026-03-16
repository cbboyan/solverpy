"""
# ATP solvers

Automated theorem provers (ATPs) for classical first-order and higher-order
logic.  All ATP solvers accept problems in
[TPTP](https://www.tptp.org) format (FOF, HOF/THF), except
[`Prover9`][solverpy.solver.atp.prover9.Prover9] which uses the LADR format.

```plantuml name="solver-atp"

abstract class solverpy.solver.shellsolver.ShellSolver
abstract class solverpy.solver.stdinsolver.StdinSolver

class solverpy.solver.atp.eprover.E extends solverpy.solver.shellsolver.ShellSolver
class solverpy.solver.atp.vampire.Vampire extends solverpy.solver.shellsolver.ShellSolver
class solverpy.solver.atp.lash.Lash extends solverpy.solver.shellsolver.ShellSolver
class solverpy.solver.atp.prover9.Prover9 extends solverpy.solver.stdinsolver.StdinSolver

```

| Solver | Binary | Format | Notes |
|---|---|---|---|
| [`E`][solverpy.solver.atp.eprover.E] | `eprover` | TPTP FOF | Pass `binary="eprover-ho"` for higher-order (THF) |
| [`Vampire`][solverpy.solver.atp.vampire.Vampire] | `vampire` | TPTP FOF/THF | Supports both first and higher order |
| [`Lash`][solverpy.solver.atp.lash.Lash] | `lash` | TPTP THF | Higher-order only; requires a modes directory via `-M` |
| [`Prover9`][solverpy.solver.atp.prover9.Prover9] | `prover9` | LADR | Reads problem from stdin; stdin-based solver |

"""

from .eprover import E
from .lash import Lash
from .vampire import Vampire
from .cvc5 import Cvc5

__all__ = ["E", "Lash", "Vampire", "Cvc5"]

