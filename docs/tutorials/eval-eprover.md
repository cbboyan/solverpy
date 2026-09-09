# 🧪 Tutorial: Evaluating E Prover Strategies

This walks through evaluating a few different `eprover` strategies on a set
of TPTP problems, end to end. See [Usage](../usage.md) first if you haven't
already, for the `sid`/`bid` concepts used below.

## ◆ 1. Bootstrap the project

```sh
$ mkdir my-eprover-eval && cd my-eprover-eval
$ solverpy init eprover
```

This creates `solverpy_db/strats/` with several bundled example strategies
(inspect them with `ls solverpy_db/strats`), and a starter
`eval-eprover.yaml`.

## ◆ 2. Pick strategies to compare

Strategy files are plain E command-line options, so you can compare any of
the bundled ones directly. A few useful ones to start with:

```sh
$ cat solverpy_db/strats/default        # (empty: E's own defaults)
$ cat solverpy_db/strats/auto           # --auto
$ cat solverpy_db/strats/autoschedule   # --auto-schedule
$ cat solverpy_db/strats/mzr02          # tuned for Mizar problems
```

`ls solverpy_db/strats` also shows a whole `mzr01`–`mzr22` family, tuned for
Mizar problems (`mzr02` is a solid, well-tested default among them),
alongside a `bls*`/`e-*` family from other automated tuning runs — good
material to compare once you're past the basics.

You can also add your own: create `solverpy_db/strats/my-strategy` and put
any `eprover` command-line options in it as plain text.

## ◆ 3. Add your benchmark problems

Create a directory of TPTP problem files, e.g.:

```sh
$ mkdir -p problems/mine
$ cp /path/to/some/*.p problems/mine/
```

Every regular file directly inside `problems/mine/` is treated as one
benchmark problem (no recursion, hidden files ignored) — that's your `bid`.

A `bid` can also point to a *file* instead of a directory. In that case the
file is a plain list of problem paths, one per line, each resolved relative
to the *directory containing the bid file itself* — handy when your
problems live in a nested/hierarchical layout you don't want to flatten.
For example, a bid file `problems/mine/subset1` (a plain text file, sitting
right inside the tree it lists):

```
category1/problemA.p
category1/problemB.p
category2/subcat/problemC.p
```

used as `benchmarks: [problems/mine/subset1]`, resolves each line relative
to `problems/mine/` — i.e. to `problems/mine/category1/problemA.p`, etc.

## ◆ 4. Write the experiment

Edit `eval-eprover.yaml` to list the strategies from step 2 and point at
your problems:

```yaml
evaluate: eprover
common:
  limit: T10
  cores: 4
evals:
  dataname: eval
  benchmarks:
    - problems/mine
  strategies:
    - default
    - auto
    - autoschedule
    - mzr02
options:
  - outputs
```

## ◆ 5. Launch it

```sh
$ solverpy run eval-eprover.yaml
```

You'll see per-strategy progress bars (solved/unsolved/errors) while it
runs. Run the same command again afterwards and notice it finishes
instantly — results are cached in `solverpy_db/` and are not recomputed
unless you `solverpy clean` first.

## ◆ 6. Inspect the results

`solverpy_db/solved/` and `solverpy_db/status/` each hold one subdirectory
per `bid`+`limit` (here `problems--mine--T10`), with one file per `sid`
inside it:

- a `solved/.../<sid>` file lists the problem names that `<sid>` solved, one
  per line;
- a `status/.../<sid>` file has one `problem<TAB>status<TAB>runtime` line
  per problem `<sid>` was run on (including unsolved ones).

Two quick tricks for `solved/`, run from inside its `problems--mine--T10/`
directory — count solved problems per strategy:

```sh
$ wc -l * | sort -n
  4 default
  7 auto
  8 mzr02
  9 autoschedule
 28 total
```

and how many *distinct* problems got solved by at least one strategy (the
union), out of 10 problems in this set:

```sh
$ sort -u * | wc -l
9
```

And in `status/`, tally how many problems ended up in each status for one
strategy, e.g. `auto`:

```sh
$ cut -f2 auto | sort | uniq -c | sort -n
      3 ResourceOut
      7 Theorem
```

(7 `Theorem` matches `auto`'s solved count above — `ResourceOut` is E's
status for hitting the `T10` cutoff.)

`solverpy_db/results/` holds the full per-problem result dictionaries
(gzip JSON), including runtime and E's parsed proof-search statistics — see
[`E.process`][solverpy.solver.atp.eprover.E.process] for exactly what's
captured.

## ◆ Next steps

- [Evaluating cvc5](eval-cvc5.md) — the same workflow for an SMT solver.
- [Training an ENIGMA model](enigma-training.md) — go from "evaluate a
  strategy" to "train E Prover's ML guidance from these problems".
- [Commands](../commands.md) — full YAML/options reference.
