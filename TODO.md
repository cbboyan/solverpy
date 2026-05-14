# Known Issues

## High

### Nested multiprocessing pools — `builder/autotune/build.py:157` + `task/launcher.py:51`
Root cause of the quadratic process issue. `build.score()` calls `evaluation.launch()`
→ `launcher.launch()` which opens a new `Pool(cores)`. If this runs inside a worker of
an outer pool (e.g. during Optuna trial evaluation), every outer worker spawns another
`cores` processes. Switching to `spawn` doesn't prevent this — it only changes how
processes are forked. The fix is to detect when already inside a worker (e.g. via a
global flag or env var) and run tasks sequentially instead of spawning a new pool.

### Solver mutable state visible across processes — `solver/solverpy.py:22–25`, `solver/solver.py:92`
`_exitcode` and `_output` are set on the solver during `solve()`. With spawn-based
multiprocessing, each worker gets its own copy so mutations are silently lost. Parent
never sees the exit code from the subprocess.

### Talker log queue never started — `task/launcher.py:48–56`
`LogTalker` does not call `log_start()` before `launching()`, so `_log_queue` is always
`None`. Tasks receive a `None` logqueue and child process logging is never redirected —
all log output from workers is silently dropped.

### Unreachable `raise` in `redirect.call()` — `tools/redirect.py:73`
`raise` after an `except` block that already unconditionally re-raises. Dead code that
suggests `KeyboardInterrupt` was meant to be handled separately (see commented-out code
nearby) but was never wired up.

## Medium

### `Limits.__lt__` returns `None` — `solver/plugins/shell/limits.py:64–65`
Returns `None` (not `False`) when limits are incomparable. Python's sort/comparison
infrastructure expects `bool` from `__lt__`; `None` causes silent incorrect comparisons
or `TypeError` depending on context. See the existing `-> bool | None` annotation which
documents the problem but doesn't fix it.

### `print()` inside `Limits.__init__` — `solver/plugins/shell/limits.py:43`
`print(e)` before re-raising bypasses the logging system. In multiprocessing workers
the output goes to the worker's stdout and is typically invisible. Use `logger.warning`.

### LogTalker wait timers grow without bound — `task/logtalker.py:106,112`
`_wait_time *= 1.1` and `_wait_total *= 2` grow indefinitely. For runs of several hours
the logging interval becomes so large that hangs are effectively invisible.

### Exception handling swallows pickling errors — `task/task.py:115–125`
`runtask` catches `Exception` but pickling failures in spawn mode are raised by the
Pool machinery **before** `runtask` runs, so they bubble up as opaque worker crashes
rather than useful error messages.

## Low / Design

### Scheduler state not reset between loop iterations — `setups/loop.py`
`LogTalker`/`SolverTalker` instances created once and reused across loop iterations.
Their internal counters (`_solved`, `_unsolved`, `_errors`) are only reset per job, not
per iteration, which can give misleading progress totals in multi-loop runs.

### Plugin order dependency implicit — `solver/pluginsolver.py:130–141`
`update()` then `finished()` is called on all decorators in sequence. Plugins that
depend on result state set by an earlier plugin's `update()` are fragile to reordering.
No documentation of expected order.

### Mutable defaults in `ShellSolver.__init__` / `StdinSolver.__init__`
`builder: "LimitBuilder" = {}` and `plugins: list["Plugin"] = []` are mutable defaults.
Same class of bug as the fixed `SolverTask` issue — safe only because these happen to
not be mutated in-place, but fragile.

# Python 3.14 fork/spawn Considerations

Python 3.14 changed the Linux default multiprocessing start method from `"fork"`
to `"forkserver"`.  Initial fixes applied, but the root cause (ISSUES.md #4:
nested pool → quadratic process blowup) that motivated the mixed `"fork"` /
`"spawn"` strategy has not been addressed.  May require revisiting the whole
approach.

Fixed so far:
- `tools/external.py` — `@external` decorator: explicit `"fork"` Process+Queue
- `benchmark/db/provider.py` — `_ProviderMaker` module-level (was local class)
- `builder/autotune/autotune.py` — `prettytuner`: explicit `"fork"` Process+Queue
- `builder/plugins/trains.py` — Manager Lock: `"fork"` context
- `builder/plugins/svm.py` — Manager Namespace: `"fork"` context
- `test_learn_loop.py` fixture — use `os.path.relpath()` for `SOLVERPY_DB` and
  `SOLVERPY_BENCHMARKS` (eprover-ho prepends `ENIGMATIC_ROOT` defaulting to `"."`;
  absolute paths produced `.//absolute/path` which fails)

Deferred: nested pool → quadratic process blowup is the root cause why `"spawn"`
was introduced.  Address that separately (see Known Issues above).

# Backlog

- automated restriction to solvable problems (force implementation)
- trains regeneration
- show best iteration in the training report
- show the initial model in the report
- reporting
- progress web api
- improve total bar ETA by not including skipped problems
- improve ETA by considering timeout
- nice ntfy messages
- solverpy command script
  - `solverpy init`
  - `solverpy init eprover`
  - `solverpy eval sid bid`
  - `solverpy tune train.in`
  - `solverpy loop bid-train bid-devel`
  - `solverpy launch setup.yaml`
  - launch stuff using command script instead of python scripts
- yaml formatter: use global variables (like `trains`) instead of references `&`
- scripts update
- simulated runs from previous outputs
- tuning phase for posneg balancing - requires full data storage
