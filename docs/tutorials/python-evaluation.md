# 🔧 Tutorial: Python API — Benchmark Evaluation

`solverpy run some.yaml` is really just a thin wrapper around the
[`setups`][solverpy.setups] Python API. Calling it directly is useful for
scripting many related experiments, or generating the setup dynamically.

## ◆ The `Setup` dict

[`Setup`][solverpy.setups.setup.Setup] is a `TypedDict` describing an
experiment; functions in [`setups`][solverpy.setups] fill in its required
keys and then launch it.

```python
from solverpy import setups

mysetup = setups.Setup(
    cores=4,
    benchmarks=["problems/bushy010"],
    strategies=["default", "auto", "autoschedule"],
    limit="T10",
)

setups.eprover(mysetup)     # choose the solver, fill in solver-specific defaults
setups.evaluation(mysetup)  # configure the evaluation pipeline (DB, cores, ...)
setups.launch(mysetup)      # run it
```

This is the exact Python equivalent of the `eval-eprover.yaml` file from
[Evaluating E Prover Strategies](eval-eprover.md) — the top-level YAML keys
map directly onto `Setup`/`Evalset` fields, and `evaluate: eprover` becomes
`setups.eprover(mysetup)`.

🤞 As with the YAML form, `solverpy_db/strats/` must already contain a file
for every sid in `strategies`, and the benchmark directories must exist —
run `solverpy init eprover` first if you haven't.

☕ After it finishes, inspect results the same way as before, under
`solverpy_db/results`, `solverpy_db/solved`, and `solverpy_db/status`.

## ◆ Swapping solvers

Only the setup function changes:

```python
setups.cvc5(mysetup)      # instead of setups.eprover(mysetup)
```

`setups` provides one such function per solver — see
[Commands](../commands.md) for the full list, or
[`setups.solver`][solverpy.setups.solver] in the API reference.

## ◆ Scripting multiple experiments

Because `mysetup` is a plain dict under the hood, it's easy to generate many
variants in a loop, e.g. sweeping over resource limits:

```python
from solverpy import setups

for limit in ["T10", "T60", "T300"]:
    setup = setups.Setup(
        cores=4,
        dataname=f"eval-{limit}",
        benchmarks=["problems/bushy010"],
        strategies=["default"],
        limit=limit,
    )
    setups.eprover(setup)
    setups.evaluation(setup)
    setups.launch(setup)
```

## ◆ Next steps

- [Training an ENIGMA model](enigma-training.md) — the ML training loop
  built on top of this same evaluation pipeline.
