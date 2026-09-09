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
- `AutoTuner` — Optuna-based hyperparameter tuning, base for the builders below
- `EnigmaModel` (and its `EnigmaSel`/`EnigmaGen`/`Enigma` variants) — builds
  LightGBM/SVM models for E Prover's ENIGMA guidance
- `Cvc5ML` — builds models for cvc5

The iterative eval/build loop runs: evaluate strategies → collect proofs →
train ML model → generate new strategies → repeat.

### Parallel Task Execution

`task/launcher.py` manages a `multiprocessing` pool. `SolverTask` wraps a
single `(solver, bid, sid, problem)` run. `Talker` subclasses report progress
(e.g., `LogTalker` logs to console/file).

### Talker Hierarchy and Progress Reporting

Talkers form a single inheritance chain plus one proxy, split across
`solverpy` and `solverpy-learn`:

```
Talker (solverpy/report/talker/talker.py)            — abstract: log queue, lifecycle hooks
  └─ LogTalker (solverpy/report/talker/logtalker.py) — log-based defaults for all events
       └─ EvalTalker (solverpy/report/talker/evaltalker.py)   — adds tqdm bars (RunningBar, SolvingBar)
            └─ LoopTalker (solverpy_learn/report/talker/looptalker.py)  — adds tuning/build bars

Talker
  └─ RemoteTalker (solverpy/report/talker/remotetalker.py)  — cross-process proxy, wraps a local Talker
```

`LogTalker._log_progress` controls verbosity: `True` → `logger.info`, `False`
→ `logger.debug`. `EvalTalker` sets it `False` and renders tqdm bars
instead. `LoopTalker` behaves like `EvalTalker` outside a tuning phase and
switches to a two-bar tuning mode (outer `tune` bar over trials, inner
`build`/`eval` bar) between `tune_begin`/`tune_end`.

`LogTalker` has log-based default implementations for all event methods,
evaluation (`eval_begin`, `eval_end`, `eval_next`, `eval_launch`,
`eval_taskdone`, `eval_done`, `eval_status`) and tuning (`tune_begin`,
`tune_end`, `tune_phase_begin`, `tune_trial_begin`, `tune_trial_done`,
`tune_phase_done`, `build_begin`, `build_step`, `build_selected`,
`build_done`, `train_data`) alike — see `talkers.md` for the full method
list and per-talker implementation matrix. These serve as fallbacks in
headless mode and as the base for `LoopTalker`'s bar overrides.

### Multiprocessing Process Layers (Tuning Pipeline)

The autotune pipeline uses three process layers:

```
main process
  └─ prettytuner child  [fork]
       └─ ATP eval workers  [spawn]
```

1. **`prettytuner`** (`builder/autotune/autotune.py`) forks a child with
   `multiprocessing.Process(target=tuner)`. Fork is used because the
   `multiprocessing.Queue` passed into `RemoteTalker` is shared with the
   child via memory copy rather than pickled.
2. **ATP eval workers** (`builder/autotune/build.py`) are spawned via
   `Pool(context="spawn")`. Spawn is used explicitly (not forkserver)
   because **forkserver cannot be started from inside a forked child
   process**.
3. `redirect.call` in `prettytuner` redirects the child's stdout/stderr at
   the file descriptor level to `autotune.log`. This means any tqdm bars
   rendered in the child would go to the log file, not the terminal — which
   is why all progress rendering happens in the parent via the queue.

### RemoteTalker

`RemoteTalker` is a generic cross-process proxy: it wraps a local `Talker`
(the real `LoopTalker`/`EvalTalker` instance living in the parent process)
and makes its methods callable from a child process. It is the only
proxying mechanism now — there is no separate self-contained tuning talker.

**Key design:**
- `__getattribute__` intercepts every public (non-underscore) method not
  listed in `LOCALS` and replaces it with a wrapper that puts
  `(name, args, kwargs)` on `_remote_queue` instead of calling it directly.
  `LOCALS` names the handful of methods that must run locally in the
  calling process (`listening_start`, `listening_stop`, `listening_handle`,
  `eval_launch`).
- A background thread in the parent (`listening_start`) drains
  `_remote_queue` and calls the real method on `_local` via
  `listening_handle`.
- `eval_launch` is special-cased: it injects `self._log_queue` into the
  child's tasks locally, then still forwards the call to the parent for
  stats.
- `prettytuner` constructs the `RemoteTalker` with a plain
  `multiprocessing.Queue()` (not a Manager queue) — safe because the child
  is forked, not spawned, so the queue does not need to be pickled.
- `__getstate__` drops `_local` (and the thread/event) from the pickled
  state, so only the queue crosses into the child; `_local` stays `None`
  there and `listening_handle` becomes a no-op.

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
  via the `RemoteTalker` queue — so log records from workers are suppressed.

To enable worker log forwarding: call `self.log_start()` in
`listening_start()`, then inject `self._log_queue` into each task in
`launching()`.

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
