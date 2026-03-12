# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Build the package
python3 -m build

# Upload to PyPI
twine upload dist/*

# Format code (PEP8, indent_width=3)
yapf -i <file>

# View current version
setuptools-git-versioning

# Generate docs
./mkdocs-build.sh      # build
./mkdocs-serve.sh      # serve locally
./mkdocs-deploy.sh     # deploy to GitHub Pages
```

There are no automated tests in this repository.

## Code Style

- **Indent width: 3 spaces** (configured in `pyproject.toml` via `[tool.yapf]`)
- Based on PEP8 style via `yapf`

## Architecture

`solverpy` provides a uniform interface to launch automated theorem provers and SMT solvers from Python, with support for parallel benchmark evaluation and ML-guided strategy construction.

### Solver Hierarchy

```
Solver (solver/solver.py)          — abstract base: solve(), run(), process()
  └─ PluginSolver (pluginsolver.py) — adds Plugin support (decorators + translators)
       └─ SolverPy (solverpy.py)    — adds resource limits, caching/simulation
            └─ ShellSolver (shellsolver.py) — runs solver as subprocess
                 └─ E, Vampire, Prover9, Lash (solver/atp/)
                 └─ Cvc5, Z3, Bitwuzla (solver/smt/)
```

**Plugins** modify solver behavior without subclassing:
- `Decorator` — wraps the shell command and post-processes results (e.g., parse TPTP/SMT status, add timing)
- `Translator` — transforms `(instance, strategy)` inputs (e.g., `(bid, problem)` pair → file path)

### Benchmark Evaluation

The evaluation pipeline (`benchmark/evaluation.py`) runs a matrix of `(solver, bid, sid)` jobs in parallel using `multiprocessing`. Results are cached in `solverpy_db/` (path overridable via `SOLVERPY_DB` env var).

**Key concepts:**
- `bid` (benchmark id): path to a problem directory or file listing problem paths. Resolved relative to `SOLVERPY_BENCHMARKS` env var (defaults to cwd).
- `sid` (strategy id): filename in `solverpy_db/strats/` containing solver CLI options.
- `Result`: dict with at minimum `status` (str) and `runtime` (float).

**DB providers** (`benchmark/db/providers/`) write output to:
- `solverpy_db/results/` — JSON (gzip) dicts of `{problem: result}` per (sid, bid)
- `solverpy_db/solved/` — list of solved problem names
- `solverpy_db/status/` — tab-separated `problem\tstatus` lines
- `solverpy_db/outputs/` — raw solver stdout (optional)

### Experiment Setup

The `Setup` TypedDict (`setups/setup.py`) is the central configuration object. Helper functions in `setups/` populate it:
- `setups.cvc5(setup)`, `setups.eprover(setup)`, etc. — set solver and static options
- `setups.evaluation(setup)` — configure for benchmark evaluation
- `setups.launch(setup)` — run everything

### ML / Builder

`builder/` contains ML model builders (`Builder` base class) for guided strategy construction:
- `EnigmaBuilder` — builds LightGBM/SVM models for E Prover's ENIGMA guidance
- `Cvc5MlBuilder` — builds models for cvc5
- `AutoTuner` — Optuna-based hyperparameter tuning

The iterative eval/build loop runs: evaluate strategies → collect proofs → train ML model → generate new strategies → repeat.

### Parallel Task Execution

`task/launcher.py` manages a `multiprocessing` pool. `SolverTask` wraps a single `(solver, bid, sid, problem)` run. `Talker` subclasses report progress (e.g., `LogTalker` logs to console/file).

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SOLVERPY_DB` | `solverpy_db` | Path to the results database directory |
| `SOLVERPY_BENCHMARKS` | `.` (cwd) | Root directory for benchmark problem resolution |
