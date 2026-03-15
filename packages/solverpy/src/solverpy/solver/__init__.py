"""
# Single problem solving

To call the solver on one problem instance, start by creating the solver object.

```python
from solverpy.solver.smt.cvc5 import Cvc5

cvc5 = Cvc5("T5")  # time limit of 5 seconds
```

The constructor argument is a resource limit string, in this case, a time limit `T` in seconds.  All solvers support `T` and additional resource limits might be available depending on the solver.  Multiple resource limits can be used (separated by `-`, like `T10-R50000`).  The limit string must, however, always start with `T`.

Then call the `solve` method:

```python
result = cvc5.solve("myproblem.smt2", "--enum-inst")
```

The first argument is the problem filename, the second is the solver-dependent strategy description (typically command line options as a string).

The result is a Python `dict` with results and statistics.  The keys and values are solver-specific.  Nevertheless, the result always contains keys `status` (with the value of type `str`) and `runtime` (type `float`).

Hint: Call `cvc5.run(p,s)` instead of `cvc5.solve(p,s)` to get the raw solver output without any processing.  Call `cvc5.command(p,s)` to output the shell command that is going to be executed to launch the solver.

"""
