"""
# SMT solvers

SMT (Satisfiability Modulo Theories) solvers for the
[SMT-LIB2](https://smtlib.cs.uiowa.edu) format.

```plantuml name="solver-smt"

abstract class solverpy.solver.shellsolver.ShellSolver

class solverpy.solver.smt.cvc5.Cvc5 extends solverpy.solver.shellsolver.ShellSolver
class solverpy.solver.smt.z3.Z3 extends solverpy.solver.shellsolver.ShellSolver
class solverpy.solver.smt.bitwuzla.Bitwuzla extends solverpy.solver.shellsolver.ShellSolver
class solverpy.solver.smt.llm2smt.Llm2smt extends solverpy.solver.shellsolver.ShellSolver

```

| Solver | Binary | Notes |
|---|---|---|
| [`Cvc5`][solverpy.solver.smt.cvc5.Cvc5] | `cvc5` | Leading SMT solver; broad theory support |
| [`Z3`][solverpy.solver.smt.z3.Z3] | `z3` | Microsoft's SMT solver; wide theory coverage |
| [`Bitwuzla`][solverpy.solver.smt.bitwuzla.Bitwuzla] | `bitwuzla` | Specialised for bit-vectors and floating point |
| [`Llm2smt`][solverpy.solver.smt.llm2smt.Llm2smt] | `llm2smt` | QF_EUF solver |

"""

from .bitwuzla import Bitwuzla
from .cvc5 import Cvc5
from .llm2smt import Llm2smt
from .z3 import Z3

__all__ = ["Bitwuzla", "Cvc5", "Llm2smt", "Z3"]
