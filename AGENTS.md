# SolverPy Monorepo Guide

This repository is a monorepo of three Python packages:

| Package | Source root | Purpose |
|---|---|---|
| `solverpy` | `packages/solverpy/src/solverpy/` | Core solver API, plugins, evaluation, database, reporting |
| `solverpy-learn` | `packages/solverpy-learn/src/solverpy_learn/` | ML builders, tuning, training data, iterative learning loops |
| `solverpy-grackle` | `packages/solverpy-grackle/src/solverpy_grackle/` | Grackle configuration portfolio optimization |

## Read Project Guidance

Before changing code, read the guidance relevant to the task:

- This file for architecture and conventions.
- [`TODO.md`](TODO.md) and [`DONE.md`](DONE.md) for current and completed work.
- [`COMMITS.md`](COMMITS.md) for commit-message structure.
- [`BUILD.md`](BUILD.md) for package and documentation commands.
- [`talkers.md`](talkers.md) for talker lifecycle methods and call sites.
- [`packages/solverpy-grackle/CLAUDE.md`](packages/solverpy-grackle/CLAUDE.md)
  and its `TODO.md` when working on Grackle.

Some older documentation contains stale names or architecture. When documents
conflict, prefer package-specific guidance, newer lifecycle notes, current
tests, and the current source code. Verify assumptions against the
implementation.

## Commands

```bash
pytest                                  # run all tests
pytest tests/test_limits.py             # run a single test file
pytest tests/test_limits.py::test_timeout_only  # run a single test
python3 -m build                        # build a package
twine upload dist/*                     # upload to PyPI
yapf -i <file>                          # format code (PEP8, indent_width=3)
setuptools-git-versioning               # view current version (from git tags)
./mkdocs-build.sh                       # build docs
./mkdocs-serve.sh                       # serve docs locally
./mkdocs-deploy.sh                      # deploy docs to GitHub Pages
```

Use `pytest`, not `python -m pytest`. Slow, learning, and Grackle tests are
excluded by default via root pytest config; run them explicitly when the task
requires them.

## Development Environment

The active packages in user site-packages are symlinks into this checkout:

- `solverpy` -> `packages/solverpy/src/solverpy`
- `solverpy_learn` -> `packages/solverpy-learn/src/solverpy_learn`
- `solverpy_grackle` -> `packages/solverpy-grackle/src/solverpy_grackle`

Source edits are immediately active. Do not reinstall packages after changes.

## YAML Scenario Tests

Three YAML scenarios serve as end-to-end integration tests. Run them from
their own directories with `solverpy clean` first.

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

Check progress via log output (printed to stdout) or
`tail -f solverpy_db/logs/*.log`.

## Code And Testing

- 3-space indentation, YAPF/PEP8 style (`[tool.yapf]` in `pyproject.toml`).
- Prefer single expressive words for function, method, and variable names.
  Avoid underscores merely to connect phrase words. Use underscores mainly for
  stable common prefixes that group related operations, with the shared
  subject first, such as `model_build`, `model_prepare`, `chunk_path`,
  `chunk_files`, `raw_path`, and `raw_files`. Prefer this grouped-prefix style
  over mixed verb-first phrases such as `build_model` and `prepare_model`.
- Follow existing module, type-annotation, setup, plugin, and talker patterns.
- Keep changes scoped and preserve unrelated working-tree changes.
- Run focused `pytest` tests for changed behavior, broadening according to
  risk.
- `SOLVERPY_DB` must be a **relative path** (or left at its default) when
  using ENIGMA ML strategies with eprover: eprover-ho prepends
  `ENIGMATIC_ROOT` (default `.`) to model paths in strategy strings, and an
  absolute `SOLVERPY_DB` produces `.//absolute/path`, which fails on Linux.
  Use `os.path.relpath()` when setting it programmatically.
- Preserve the intentional multiprocessing context split: normal evaluation
  uses `forkserver`, ATP evaluation inside tuning uses `spawn`, and selected
  data-loading/compression paths use `fork`.

For documentation work, follow the mkdocs/mkdocstrings conventions in the
repository and inspect `.claude/skills/document-code/SKILL.md`.

## Grackle Rules

- New or updated Grackle runners must use `solverpy`; follow the current
  `SolverPyRunner`-based implementations.
- New or updated parameter domains must subclass `GrackleDomain` or
  `CustomDomain`.
- Consult the Grackle package's `CLAUDE.md` and `TODO.md`; parts of its older
  README and root guidance describe pre-migration architecture.

## Architecture (`solverpy` package)

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
- `Decorator` — wraps the shell command and post-processes results (e.g.,
  parse TPTP/SMT status, add timing)
- `Translator` — transforms `(instance, strategy)` inputs (e.g., `(bid,
  problem)` pair → file path)

### Benchmark Evaluation

The evaluation pipeline (`benchmark/evaluation.py`) runs a matrix of
`(solver, bid, sid)` jobs in parallel using `multiprocessing`. Results are
cached in `solverpy_db/` (path overridable via `SOLVERPY_DB` env var).

**Key concepts:**
- `bid` (benchmark id): path to a problem directory or file listing problem
  paths. Resolved relative to `SOLVERPY_BENCHMARKS` env var (defaults to cwd).
- `sid` (strategy id): filename in `solverpy_db/strats/` containing solver
  CLI options.
- `Result`: dict with at minimum `status` (str) and `runtime` (float).

**DB providers** (`benchmark/db/providers/`) write output to:
- `solverpy_db/results/` — JSON (gzip) dicts of `{problem: result}` per (sid, bid)
- `solverpy_db/solved/` — list of solved problem names
- `solverpy_db/status/` — tab-separated `problem\tstatus` lines
- `solverpy_db/outputs/` — raw solver stdout (optional)

### Experiment Setup

The `Setup` TypedDict (`setups/setup.py`) is the central configuration
object. Helper functions in `setups/` populate it:
- `setups.cvc5(setup)`, `setups.eprover(setup)`, etc. — set solver and static
  options
- `setups.evaluation(setup)` — configure for benchmark evaluation
- `setups.launch(setup)` — run everything

### ML / Builder (`solverpy-learn` package)

`builder/` contains ML model builders (`Builder` base class) for guided
strategy construction:
- `EnigmaBuilder` — builds LightGBM/SVM models for E Prover's ENIGMA guidance
- `Cvc5MlBuilder` — builds models for cvc5
- `AutoTuner` — Optuna-based hyperparameter tuning

The iterative eval/build loop runs: evaluate strategies → collect proofs →
train ML model → generate new strategies → repeat.

### Parallel Task Execution

`task/launcher.py` manages a `multiprocessing` pool. `SolverTask` wraps a
single `(solver, bid, sid, problem)` run. `Talker` subclasses report progress
(e.g., `LogTalker` logs to console/file).

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

`LogTalker._log_progress` controls verbosity: `True` → `logger.info`, `False`
→ `logger.debug`. `SolverTalker` sets it `False` and renders tqdm bars
instead. `TuneTalker` overrides it with the `headless` flag after
`super().__init__()`.

`LogTalker` has log-based default implementations for all event methods
including tuning events (`trials`, `trying`, `tried`, `trialed`, `building`,
`iteration`, `built`, `tuning`, `tuned`). These serve as fallbacks in
headless mode and as the base for `TuneTalker`'s bar overrides.

### Multiprocessing Process Layers (Tuning Pipeline)

The autotune pipeline uses three process layers:

```
main process
  └─ prettytuner child  [fork]
       └─ ATP eval workers  [spawn]
```

1. **`prettytuner`** (`builder/autotune/autotune.py`) forks a child with
   `multiprocessing.Process(target=tuner)`. Fork is used because `TuneTalker`
   holds a plain `multiprocessing.Queue` which is not picklable — fork
   shares it via memory copy.
2. **ATP eval workers** (`builder/autotune/build.py`) are spawned via
   `Pool(context="spawn")`. Spawn is used explicitly (not forkserver)
   because **forkserver cannot be started from inside a forked child
   process**.
3. `redirect.call` in `prettytuner` redirects the child's stdout/stderr at
   the file descriptor level to `autotune.log`. This means any tqdm bars
   rendered in the child would go to the log file, not the terminal — which
   is why all progress rendering happens in the parent via the queue.

### TuneTalker Architecture

`TuneTalker` is a self-contained talker for the tuning pipeline that
replaces the former `RemoteTalker(SolverTalker()) + AutotuneListener` pair.

**Key design:**
- Holds a plain `multiprocessing.Queue` (works because the child is forked,
  not spawned — no pickling needed).
- `__getattribute__` intercepts every method in `REMOTES` in the child and
  puts `(name, args, kwargs)` on the queue instead of calling the real
  method.
- The parent's listening thread calls `object.__getattribute__(self, name)`
  to bypass the proxy and invoke the real handler.
- `wait()` blocks on `_result_event` until the child calls `result(val)`.
- `listening_start()` does **not** call `log_start()` — no Manager queue, no
  log queue infrastructure.
- Worker `task.logqueue` is intentionally `None`; child worker logging is
  suppressed. To enable: call `self.log_start()` in `listening_start()` and
  inject `self._log_queue` into tasks in `launching()`.

### Log Queue Mechanism

`Talker._log_queue` / `QueueListener` is built-in infrastructure for routing
child process `logging` records to the parent. It is currently **inactive
by design**:

- `listening_start()` (which calls `log_start()` to create the queue) is not
  called in the regular evaluation path.
- Worker tasks receive `task.logqueue = None`; workers configure their own
  logging normally.
- In the tuning pipeline, child output is intentionally redirected to
  `autotune.log` via `redirect.call` and structured progress events travel
  via the `TuneTalker` queue — so log records from workers are suppressed.

To enable worker log forwarding: call `self.log_start()` in
`listening_start()`, then inject `self._log_queue` into each task in
`launching()`.

### RemoteTalker

`RemoteTalker` is a generic cross-process proxy that wraps any local
`Talker` and makes its methods callable from a child process. It is not used
in the tuning pipeline (replaced by `TuneTalker`) but remains available for
other uses.

- `queue=None` (default): creates a Manager queue via forkserver —
  picklable into spawn workers.
- `queue=<queue>`: uses the provided queue directly — suitable when the
  child is forked and pickling is not needed.
- `_remote_manager` is stored as an instance attribute to prevent GC of the
  Manager server process.
- `log_start`, `log_stop`, `log_config` are **not** in `REMOTES` — they must
  execute locally on the `RemoteTalker` instance (or in the child process),
  not be forwarded to `_local`.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SOLVERPY_DB` | `solverpy_db` | Path to the results database directory |
| `SOLVERPY_BENCHMARKS` | `.` (cwd) | Root directory for benchmark problem resolution |
| `ENIGMATIC_ROOT` | `.` (cwd) | eprover-ho model root: prepended to model paths in strategy strings |

## Versioning

Versioning is automated via a `post-commit` git hook (`.git/hooks/post-commit`)
using the `gitautoversion` package (also in this repo). After every commit it:

1. Regenerates `CHANGELOG.md` from the git log.
2. Amends the commit to include the updated changelog (a lockfile prevents
   infinite recursion).
3. Sets version tags on commits.

Therefore:

- Never manually edit `CHANGELOG.md` or version tags.
- The commit hash printed by the initial `git commit` will differ from the
  final hash after the hook runs — this is expected. `git push` always
  pushes the amended commit; `git log` shows the correct final hash.
- Inspect the final `HEAD` before reporting or pushing.
- Do not commit or push unless the user asks.

### Commit Style

Use Conventional Commit-style subjects:

```text
<type>[optional scope]: <description>
```

Match recent repository history: a concise subject, with an explanatory body
for non-trivial changes. When an AI assistant materially authors a commit,
add the appropriate `Co-Authored-By` trailer for the assistant that actually
did the work — never falsely attribute work to Claude or another assistant.

This repository uses a custom exclamation-mark version policy, not standard
Conventional Commits SemVer behavior:

- `type:` creates no version tag.
- `type!:` bumps PATCH.
- `type!!:` bumps MINOR.
- `type!!!:` bumps MAJOR.

Never introduce `!`, `!!`, or `!!!` in a commit type without explicit
agreement from the user for that specific version bump.

## Working Tree

Generated or experiment files may be present. Do not add, remove, or modify
unrelated files. In particular, treat existing untracked files under
`scripts/` and files such as `talkers.html` as user-owned unless the task
explicitly targets them.
