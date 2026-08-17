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
class solverpy.solver.smt.primo.Primo extends solverpy.solver.shellsolver.ShellSolver
class solverpy.solver.smt.opensmt.Opensmt extends solverpy.solver.shellsolver.ShellSolver
class solverpy.solver.smt.yices.Yices extends solverpy.solver.shellsolver.ShellSolver

```

| Solver | Binary | Notes |
|---|---|---|
| [`Cvc5`][solverpy.solver.smt.cvc5.Cvc5] | `cvc5` | Leading SMT solver; broad theory support |
| [`Z3`][solverpy.solver.smt.z3.Z3] | `z3` | Microsoft's SMT solver; wide theory coverage |
| [`Bitwuzla`][solverpy.solver.smt.bitwuzla.Bitwuzla] | `bitwuzla` | Specialised for bit-vectors and floating point |
| [`Llm2smt`][solverpy.solver.smt.llm2smt.Llm2smt] | `llm2smt` | QF_EUF solver |
| [`Primo`][solverpy.solver.smt.primo.Primo] | `primo` | QF_LRA and QF_UF solver |
| [`Opensmt`][solverpy.solver.smt.opensmt.Opensmt] | `opensmt` | SMT solver with interpolation and proofs |
| [`Yices`][solverpy.solver.smt.yices.Yices] | `yices-smt2` | Yices 2; SMT-LIB2 front end of `yices` |

"""

from .bitwuzla import Bitwuzla
from .cvc5 import Cvc5
from .llm2smt import Llm2smt
from .opensmt import Opensmt
from .primo import Primo
from .yices import Yices
from .z3 import Z3

__all__ = ["Bitwuzla", "Cvc5", "Llm2smt", "Opensmt", "Primo", "Yices", "Z3"]
