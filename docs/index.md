# 🏠 SolverPy

!!! quote intro ""
    `SolverPy` is a generic Python interface for **evaluation** and **machine
    learning** of automated theorem provers (ATPs) and SMT (Satisfiability
    Modulo Theories) solvers. Most everyday work happens through the
    `solverpy` shell command and YAML experiment files — no Python code
    required — though a full Python API is available too.

**v2.1.2** · [GitHub](https://github.com/cbboyan/solverpy) · [Changelog](https://github.com/cbboyan/solverpy/blob/main/CHANGELOG.md)

```sh
$ pip install solverpy
```

See [Install](install.md) for other ways to install SolverPy (from source,
solver binaries, `solverpy-learn`).

## 🎁 What SolverPy gives you

- A single `solverpy` command that runs an experiment described by a YAML
  file, such as evaluating a set of E Prover strategies on a set of problems.
- A uniform interface across ATP and SMT solvers — [`E`][solverpy.solver.atp.eprover],
  [`Vampire`][solverpy.solver.atp.vampire], [`Prover9`][solverpy.solver.atp.prover9],
  [`Lash`][solverpy.solver.atp.lash], [`cvc5`][solverpy.solver.smt.cvc5],
  [`Z3`][solverpy.solver.smt.z3], [`Opensmt`][solverpy.solver.smt.opensmt], and
  more — so the same experiment, database, and reporting code works for all
  of them.
- A results **database** (`solverpy_db/`) that caches every run: re-running
  an experiment reuses cached results instead of re-solving.
- **Machine-learning guidance** via the companion `solverpy-learn` package:
  `enigma` trains E Prover's ENIGMA clause-selection models, and `cvc5ml`
  trains ML-enhanced cvc5 strategies, both as iterative evaluate → train →
  re-evaluate loops.

## 🚀 What's new in v2.1.2 (2026-09-04)

- Added the `SPASS-SATT` SMT solver plugin.
- Wired the new `RunHash` status decorator into `E` and `Primo`, for
  reproducibility checks across runs.
- Fixed E's `--cpu-limit`/`--soft-cpu-limit` ordering under `--auto-schedule`.

See the [full changelog](https://github.com/cbboyan/solverpy/blob/main/CHANGELOG.md) for every release.

## 🗺️ Where to go next

- [Install](install.md) — installing SolverPy and the solver binaries it drives.
- [Usage](usage.md) — the `solverpy` command, your first YAML experiment, and the `sid`/`bid` concepts.
- [Commands](commands.md) — full reference for every `solverpy` subcommand.
- [Tutorials](tutorials/eval-eprover.md) — step-by-step walkthroughs, including the Python API.
