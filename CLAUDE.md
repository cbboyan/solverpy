# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_limits.py

# Run a single test
pytest tests/test_limits.py::test_timeout_only

# Build the package
python3 -m build

# Upload to PyPI
twine upload dist/*

# Format code (PEP8, indent_width=3)
yapf -i <file>

# View current version (derived from git tags via gitautoversion)
setuptools-git-versioning

# Generate docs
./mkdocs-build.sh      # build
./mkdocs-serve.sh      # serve locally
./mkdocs-deploy.sh     # deploy to GitHub Pages
```

There are no automated tests in this repository.

## YAML Scenario Tests

Three YAML scenarios serve as end-to-end integration tests. Run them from their own directories with `solverpy clean` first.

**Eval yaml tests** — test E Prover and llm2smt evaluation:
```bash
cd /home/yan/repos/cbboyan/work26/solverpy/eval
echo "y" | solverpy clean && solverpy run eval-eprover.yml
echo "y" | solverpy clean && solverpy run eval-llm2smt.yml
```

**Tune yaml test** — tests ENIGMA tuning loop (eval → train → tune → loop):
```bash
cd /home/yan/repos/cbboyan/work26/solverpy/loop
echo "y" | solverpy clean && solverpy run loop-eprover-atpeval.yml
```

Check progress via log output (printed to stdout) or `tail -f solverpy_db/logs/*.log`.

## Versioning

Versioning is automated via a `post-commit` git hook (`.git/hooks/post-commit`) using the `gitautoversion` package (also in this repo). After every commit it:
1. Regenerates `CHANGELOG.md` from the git log
2. Amends the commit to include the updated changelog (a lockfile prevents infinite recursion)
3. Sets version tags on commits

Do not manually edit `CHANGELOG.md` or version tags — they are managed automatically.

The commit hash shown by `git commit` will differ from the final hash after the hook runs — this is expected. `git push` always pushes the amended commit, and `git log` will show the correct final hash.

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

### Talker Hierarchy and Progress Reporting

Talkers form a single inheritance chain plus one proxy:

```
Talker (task/talker.py)               — abstract: log queue, lifecycle hooks
  └─ LogTalker (task/logtalker.py)    — log-based defaults for all events
       └─ SolverTalker (task/solvertalker.py)  — adds tqdm bars (RunningBar, SolvingBar)
            └─ TuneTalker (autotune/tunetalker.py)  — self-contained tuning talker

Talker
  └─ RemoteTalker (task/remotetalker.py)  — cross-process proxy, wraps a local Talker
```

`LogTalker._log_progress` controls verbosity: `True` → `logger.info`, `False` → `logger.debug`. `SolverTalker` sets it `False` and renders tqdm bars instead. `TuneTalker` overrides it with the `headless` flag after `super().__init__()`.

`LogTalker` has log-based default implementations for all event methods including tuning events (`trials`, `trying`, `tried`, `trialed`, `building`, `iteration`, `built`, `tuning`, `tuned`). These serve as fallbacks in headless mode and as the base for `TuneTalker`'s bar overrides.

### Multiprocessing Process Layers (Tuning Pipeline)

The autotune pipeline uses three process layers:

```
main process
  └─ prettytuner child  [fork]
       └─ ATP eval workers  [spawn]
```

1. **`prettytuner`** (`builder/autotune/autotune.py`) forks a child with `multiprocessing.Process(target=tuner)`. Fork is used because `TuneTalker` holds a plain `multiprocessing.Queue` which is not picklable — fork shares it via memory copy.

2. **ATP eval workers** (`builder/autotune/build.py`) are spawned via `Pool(context="spawn")`. Spawn is used explicitly (not forkserver) because **forkserver cannot be started from inside a forked child process**.

3. `redirect.call` in `prettytuner` redirects the child's stdout/stderr at the file descriptor level to `autotune.log`. This means any tqdm bars rendered in the child would go to the log file, not the terminal — which is why all progress rendering happens in the parent via the queue.

### TuneTalker Architecture

`TuneTalker` is a self-contained talker for the tuning pipeline that replaces the former `RemoteTalker(SolverTalker()) + AutotuneListener` pair.

**Key design:**
- Holds a plain `multiprocessing.Queue` (works because the child is forked, not spawned — no pickling needed).
- `__getattribute__` intercepts every method in `REMOTES` in the child and puts `(name, args, kwargs)` on the queue instead of calling the real method.
- The parent's listening thread calls `object.__getattribute__(self, name)` to bypass the proxy and invoke the real handler.
- `wait()` blocks on `_result_event` until the child calls `result(val)`.
- `listening_start()` does **not** call `log_start()` — no Manager queue, no log queue infrastructure.
- Worker `task.logqueue` is intentionally `None`; child worker logging is suppressed. To enable: call `self.log_start()` in `listening_start()` and inject `self._log_queue` into tasks in `launching()`.

### Log Queue Mechanism

`Talker._log_queue` / `QueueListener` is built-in infrastructure for routing child process `logging` records to the parent. It is currently **inactive by design**:

- `listening_start()` (which calls `log_start()` to create the queue) is not called in the regular evaluation path.
- Worker tasks receive `task.logqueue = None`; workers configure their own logging normally.
- In the tuning pipeline, child output is intentionally redirected to `autotune.log` via `redirect.call` and structured progress events travel via the `TuneTalker` queue — so log records from workers are suppressed.

To enable worker log forwarding: call `self.log_start()` in `listening_start()`, then inject `self._log_queue` into each task in `launching()`.

### RemoteTalker

`RemoteTalker` is a generic cross-process proxy that wraps any local `Talker` and makes its methods callable from a child process. It is not used in the tuning pipeline (replaced by `TuneTalker`) but remains available for other uses.

- `queue=None` (default): creates a Manager queue via forkserver — picklable into spawn workers.
- `queue=<queue>`: uses the provided queue directly — suitable when the child is forked and pickling is not needed.
- `_remote_manager` is stored as an instance attribute to prevent GC of the Manager server process.
- `log_start`, `log_stop`, `log_config` are **not** in `REMOTES` — they must execute locally on the `RemoteTalker` instance (or in the child process), not be forwarded to `_local`.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SOLVERPY_DB` | `solverpy_db` | Path to the results database directory |
| `SOLVERPY_BENCHMARKS` | `.` (cwd) | Root directory for benchmark problem resolution |
| `ENIGMATIC_ROOT` | `.` (cwd) | eprover-ho model root: prepended to model paths in strategy strings |

**Important:** `SOLVERPY_DB` must be set as a **relative path** (or left at its default) when using ENIGMA ML strategies with eprover. eprover-ho prepends `ENIGMATIC_ROOT` (defaulting to `.`) to model paths in strategy strings. If `SOLVERPY_DB` is absolute, the concatenation produces `.//absolute/path` which fails on Linux. Use `os.path.relpath()` when setting `SOLVERPY_DB` programmatically.
