# `solverpy`: Automated Solver Interface for Python

`solverpy` is a Python package implementing a common interface to launch an automated logic solver from Python and process its output.
Currently supported solvers are:

* E Prover (solver.atp.eprover.E)
* Vampire (solver.atp.vampire.Vampire)
* Prover9 (solver.atp.prover9.Prover9)
* Lash (solver.atp.lash.Lash)
* cvc5 (solver.smt.cvc5.Cvc5)
* Z3 (solver.smt.z3.Z3)
* Bitwuzla (solver.smt.bitwuzla.Bitwuzla)

Note that the solver binaries are not part of this Python package and must be installed separately by the user.
The respective binaries must be (by default) in `PATH` if you wish to use them.

## Installation

```bash
$ pip install solverpy
```

## Simple usage

Simply create a solver object:

```python
from solverpy.solver.smt.cvc5 import Cvc5

cvc5 = Cvc5("T5")  # time limit of 5 seconds
```

The argument is a resource limit string, in this case a time limit `T` in seconds.  All solvers support `T` and additional resource limits are solver-specific.
The limit string must, however, always start with `T`.

And call the `solve` method:

```python
result = cvc5.solve("myproblem.smt2", "--enum-inst")
```

The first argument is the filename, the second is the solver-dependent strategy description (typically command line options as a string).

The result is a Python `dict` with results and statistics.  The keys and values are solver-specific.  The result always contains keys `status` (with the value of type `str`) and `runtime` (type `float`).
