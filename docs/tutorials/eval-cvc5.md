# ⚗️ Tutorial: Evaluating cvc5 Strategies

The same workflow as [Evaluating E Prover](eval-eprover.md), for the SMT
solver `cvc5`.

## ◆ 1. Bootstrap the project

```sh
$ mkdir my-cvc5-eval && cd my-cvc5-eval
$ solverpy init cvc5
```

This creates `solverpy_db/strats/` populated with several bundled cvc5
strategies (`ls solverpy_db/strats`), each a plain-text line of `cvc5`
command-line options, e.g.:

```sh
$ cat solverpy_db/strats/smtcomp01
--simplification=none --enum-inst
```

## ◆ 2. Add benchmark problems

Download a ready-made set of SMT-LIB2 problems (translated from the Mizar
Mathematical Library) together with a few extra example strategies tuned
for them:

```sh
$ wget https://cbboyan.github.io/solverpy/example.tar.gz
# or: curl -LO https://cbboyan.github.io/solverpy/example.tar.gz
$ tar xzf example.tar.gz --strip-components=1
```

This adds `problems/` (your `bid`) and a few more strategy files —
`buzzard`, `sparrow`, `chickadee`, `enum` — into `solverpy_db/strats/`,
alongside the bundled `smtcomp*` ones from step 1.

## ◆ 3. Pick strategies to compare

Any of the bundled `smtcomp*` strategies work directly, as do `buzzard`,
`sparrow`, and `chickadee` from the downloaded set — or add your own by
creating a new file under `solverpy_db/strats/` with the cvc5 options you
want to try.

## ◆ 4. Write the experiment

```yaml
evaluate: cvc5
common:
  limit: T10
  cores: 4
evals:
  dataname: eval
  benchmarks:
    - problems
  strategies:
    - buzzard
    - sparrow
    - chickadee
options:
  - outputs
```

Save this as `eval-cvc5.yaml`.

## ◆ 5. Launch it

```sh
$ solverpy run eval-cvc5.yaml
```

As before, results are cached: re-running the same command is instant unless
you `solverpy clean` first.

## ◆ 6. Inspect the results

```sh
$ cat solverpy_db/status/problems--T10/buzzard
$ cat solverpy_db/solved/problems--T10/sparrow
```

The full per-problem results (gzip JSON in `solverpy_db/results/`) include
cvc5's own `--stats`/`--stats-internal` counters — see
[`Cvc5.process`][solverpy.solver.smt.cvc5.Cvc5.process] for what's captured,
and an explicit `timeout` status when cvc5 reports being interrupted.

## ◆ Next steps

- [Training an ENIGMA model](enigma-training.md) — the ML training loop, for E Prover.
- [Python API: benchmark evaluation](python-evaluation.md) — the same workflow, called from Python instead of YAML.
- [Commands](../commands.md) — full YAML/options reference.
