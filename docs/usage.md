# 🧭 Usage

## ◆ Bootstrap a project

```sh
$ solverpy init eprover
```

`solverpy init <solver>` creates `solverpy_db/strats/` in the current
directory, populates it with a few bundled example strategies for
`<solver>`, and drops a starter `eval-<solver>.yaml` experiment file next to
it. Run `solverpy init` with no argument to bootstrap all bundled solvers at
once.

## ◆ `sid` and `bid`

Every experiment evaluates a set of _strategies_ on a set of _benchmark
problems_:

- A **strategy id** (`sid`) is just a filename in `solverpy_db/strats/`. Its
  content is the solver's command-line options — it can even be empty, for
  the solver's own defaults. So `strategies: [default]` in an experiment
  means "use the options in `solverpy_db/strats/default`".
- A **benchmark id** (`bid`) is a path, relative to the current directory,
  to a directory of problem files, e.g. `myproblems/`. (A `bid` can also
  point to a file listing problem paths instead of a directory — see
  [Tutorials](tutorials/eval-eprover.md) for that case.)

## ◆ Your first experiment

`solverpy init eprover` creates the strategy files above and a starter
`eval-eprover.yaml`:

```yaml
evaluate: eprover
common:
  limit: T1      # resource limit (T=time, M=memory in GB, e.g. T10-M4)
  cores: 4
evals:
  dataname: eval # label for output directories
  benchmarks:
    - problems/bushy010
  strategies:
    - default
options:
  - outputs      # keep raw solver output files
```

Put your problem files where `benchmarks:` points (here `problems/bushy010`),
then launch the evaluation:

```sh
$ solverpy run eval-eprover.yaml
```

Results land under `solverpy_db/results`, `solverpy_db/solved`, and
`solverpy_db/status` — see [Commands](commands.md) for the full database
layout. Re-running the same command reuses the cached results instead of
re-solving everything.

## ◆ Try it on real problems

Rather than supplying your own, download a small set of real TPTP problems
to fill in `problems/bushy010` from the experiment above:

```sh
$ wget https://cbboyan.github.io/solverpy/eprover-example.tar.gz
# or: curl -LO https://cbboyan.github.io/solverpy/eprover-example.tar.gz
$ tar xzf eprover-example.tar.gz
```

This extracts `problems/bushy010/` directly, matching the `benchmarks:`
entry already in `eval-eprover.yaml` — so you can launch it right away:

```sh
$ solverpy run eval-eprover.yaml
```

There's also a similar downloadable set of SMT-LIB2 problems for cvc5 — see
[Evaluating cvc5](tutorials/eval-cvc5.md).

## ◆ Next steps

This covers the basics. For step-by-step walkthroughs — evaluating specific
E and cvc5 strategies, training an ENIGMA model, and using the Python API
directly — see [Tutorials](tutorials/eval-eprover.md).
