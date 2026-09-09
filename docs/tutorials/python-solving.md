# 💡 Tutorial: Python API — Solving a Single Problem

For one-off use, or when embedding SolverPy in a larger Python program, you
can call a solver directly without going through a YAML experiment.

## ◆ Create a solver object

```python
from solverpy.solver.smt.cvc5 import Cvc5

cvc5 = Cvc5("T5")  # time limit of 5 seconds
```

The constructor argument is a resource limit string: `T` for time (seconds)
is supported by every solver, and some solvers accept additional limits
(e.g. `M` for memory, in GB). Multiple limits can be combined with `-`, like
`T10-M4`; the string must always start with `T`.

## ◆ Solve a problem

```python
result = cvc5.solve("myproblem.smt2", "--enum-inst")
```

The first argument is the problem file; the second is the solver-specific
*strategy* — typically a command-line-options string, exactly what you would
otherwise put in a `solverpy_db/strats/` sid file.

The result is a `dict`; its keys and values are solver-specific, but it is
always guaranteed to contain at least `status` (`str`) and `runtime`
(`float`).

```python
print(result["status"], result["runtime"])
```

💡 Call `cvc5.run(p, s)` instead of `cvc5.solve(p, s)` to get the raw solver
output without any post-processing.

💡 Call `cvc5.command(p, s)` to see the shell command that would be
executed, without running anything.

## ◆ Other solvers

The same pattern works for every solver — only the import and the
strategy syntax change:

```python
from solverpy.solver.atp.eprover import E

e = E("T10")
result = e.solve("myproblem.p", "--auto-schedule")
```

See [`solver`][solverpy.solver] for the full list of available solver
classes.

## ◆ Next steps

- [Python API: benchmark evaluation](python-evaluation.md) — the same
  solvers, run over many problems and strategies in parallel with database
  caching.
