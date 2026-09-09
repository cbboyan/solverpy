# 🧠 Tutorial: Training an ENIGMA Model

ENIGMA trains a machine-learning model that guides E Prover's clause
selection, by repeating: evaluate a strategy → collect proofs → train a
model from them → generate a new, ML-enhanced strategy → re-evaluate. This
requires the `solverpy-learn` package and an `eprover-ho` binary built with
ENIGMA's ML features.

## ◆ 1. Prepare the database

```sh
$ mkdir my-enigma-loop && cd my-enigma-loop
$ solverpy init eprover
```

As in [Evaluating E](eval-eprover.md), this gives you `solverpy_db/strats/`
with bundled strategies. We'll use one of these as the *base strategy* that
ENIGMA learns to improve.

🗒️ **Not every strategy works as a base strategy.** ENIGMA folds its model
into an existing clause-evaluation-function definition (E's `-H` option), so
the base strategy must define one explicitly. `auto` (and `--auto-schedule`)
pick a heuristic internally and don't expose a `-H` string, so they can't be
used here. `mzr02` (and the rest of the `mzr*` family, tuned for Mizar
problems) does define one — use that instead.

## ◆ 2. Prepare the problems

```sh
$ mkdir -p problems
$ cp -r /path/to/some/problems problems/mine
```

Unlike a plain evaluation, a loop needs proofs to train from, so pick a
problem set your base strategy can actually solve a good fraction of.

## ◆ 3. Write the loop YAML

```yaml
loop: enigma
strategy: mzr02

sel_features: "C(l,x,s,r,v[b=2048],h,c,d,t,a):M:F:S:G"
loops: 3

common:
  limit: T5
  cores: 4
  binary: eprover-ho       # ENIGMA needs the ML-enabled build

evals:
  dataname: enigma/train
  benchmarks:
    - problems/mine

options:
  - outputs
  - debug-trains

tune:
  phases: "l"              # which LightGBM parameter groups to tune (l: leaves)
  atpeval: true
  timeout: null
  iters: 8                 # Optuna trials per loop iteration
  min_leaves: 8
  max_leaves: 256
  init_params:
    metric: auc
    num_round: 250
    num_leaves: 4
```

Save this as `loop-eprover-enigma.yaml`.

- `strategy:` is the base sid both trained on and refined.
- `sel_features:` picks E's clause-selection feature set (see E's own
  documentation for the feature-string syntax); a `gen_features:` key is
  also accepted for the clause-generation model and defaults to none.
- `tune.phases` controls which LightGBM hyperparameter groups Optuna tunes
  each loop iteration, one after another: `l`=leaves (`num_leaves`),
  `b`=bagging, `r`=regularization, `m`=`min_data`, `d`=`max_depth`,
  `e`=`learning_rate`, `w`=positive/negative sample weight ratio (see
  `solverpy tune --help` in [Commands](../commands.md)). `iters:` is a
  total trial budget split evenly across the listed phases (so `"l"` alone
  gives leaves the full `iters:` trials, while the CLI default `"l:b:m:r"`
  spreads the same budget across all four, fewer trials each, in exchange
  for tuning more parameter groups) — bump `iters:` accordingly if you add
  phases.

## ◆ 4. Launch it

```sh
$ solverpy run loop-eprover-enigma.yaml
```

Each of the `loops:` iterations: evaluates the current strategy on `evals:`,
collects proofs from the successful runs, trains a LightGBM model from them
(`solverpy_db/trains/`, `solverpy_db/models/`), derives new ml-enhanced
strategies from the trained model, and evaluates those.

## ◆ 5. What ends up in `solved/`

Even a minimal, fast config — `loops: 1`, `tune.iters: 2`, `limit: T5` —
exercises the same mechanism as the fuller settings above, just quicker. On
the same 10-problem TPTP set as [Evaluating E](eval-eprover.md):

```sh
$ cd solverpy_db/solved/problems--mine--T5
$ wc -l * | sort -n
   8 mzr02
   8 mzr02-coop@sel=enigma--train--loop00--sel_Clxsrvb2048hcdtaMFSG
   ...
   8 mzr02-solo@sel=enigma--train--loop00--sel_Clxsrvb2048hcdtaMFSG
   ...
  72 total
```

(With `loops: 3`/`iters: 8` as in the YAML above, this list is the same
shape but longer — `loop01`/`loop02` subdirectories, and more `--opt--`
entries per loop.)

That's more than just "the base strategy plus one new one":

- `mzr02` is the unmodified base strategy, evaluated for reference.
- `mzr02-coop@sel=...` and `mzr02-solo@sel=...` are the two ways E can use a
  trained model during search — *cooperatively* alongside the original
  heuristic, or *solo*, driving selection on its own. These are synthesized
  sid strings (embedding the model path), not files under
  `solverpy_db/strats/`.
- The rest of the lines (elided above as `...`), each strategy name suffixed
  `--opt--init` or `--opt--01-leaves--modelNNNN`, are Optuna trials: one
  entry per trial (`init` plus one per `iters:`) — each candidate model gets
  evaluated so the tuner can pick the best-performing one.

On this tiny toy set all nine variants solve the same 8 of 10 problems — one
loop and two trials aren't enough data to show a real improvement over the
base strategy; that's expected here, not a sign anything is broken. With
more problems, more loops, and more tuning trials, later strategies should
start pulling ahead.

```sh
$ ls solverpy_db/models/enigma/train/loop00/sel_Clxsrvb2048hcdtaMFSG/
enigma.map  model.lgb  opt/
```

Re-running `solverpy run loop-eprover-enigma.yaml` picks up cached
evaluation results and models rather than recomputing them — `solverpy
clean` first if you want a fresh run.

## ◆ Adding a development set

The example above trains and evaluates on the same problem set (`evals:`).
For anything beyond a quick trial run, add a separate **development** set
(`devels:`) — problems held out from training, used to check that the
trained model actually generalizes rather than just memorizing its own
training proofs:

```yaml
evals:
  dataname: enigma/train
  benchmarks:
    - problems/mine

devels:
  dataname: enigma/devel
  benchmarks:
    - problems/heldout
```

With `devels:` present, each loop iteration additionally evaluates every
candidate strategy on `problems/heldout`, so the reported solved-count
improvements reflect problems the model never saw proofs from during
training.

## ◆ Next steps

- [Commands](../commands.md) — `solverpy tune`/`compress`/`decompress`/`deconflict`/`filter` reference for working with training data directly.
