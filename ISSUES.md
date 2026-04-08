# Code Issues

Issues found during code review, roughly ordered by priority.

---

## Critical

### ~~1. Debug code left in `launcher.launch()` — `task/launcher.py:57–71`~~ ✓ FIXED
~~Writes to `~/debug.log` and iterates all solver attributes with `dir()` on every call to
`launch()`. Creates unbounded log growth and has a measurable performance impact.~~

### ~~2. Mutable default argument in `SolverTask.__init__` — `task/solvertask.py:28`~~ ✓ FIXED
~~`calls: list[...] = []` is shared across all instances created without an explicit
`calls` argument. Plugin calls registered in one task leak into all subsequent tasks.~~

### 3. File resource leak in `Outputs.write()` — `solver/plugins/db/outputs.py:72–76`
`fw.close()` is not inside a `with` block — if `fw.write()` raises, the file descriptor
leaks. Under heavy evaluation load this can exhaust system file descriptors.

---

## High

### 4. Nested multiprocessing pools — `builder/autotune/build.py:157` + `task/launcher.py:51`
Root cause of the quadratic process issue. `build.score()` calls `evaluation.launch()`
→ `launcher.launch()` which opens a new `Pool(cores)`. If this runs inside a worker of
an outer pool (e.g. during Optuna trial evaluation), every outer worker spawns another
`cores` processes. Switching to `spawn` doesn't prevent this — it only changes how
processes are forked. The fix is to detect when already inside a worker (e.g. via a
global flag or env var) and run tasks sequentially instead of spawning a new pool.

### 5. Manager queue lifecycle — `task/talker.py:87`
`mp.get_context("spawn").Manager().Queue()` creates a Manager subprocess that is never
cleaned up if the program crashes or `log_stop()` is not called. Multiple calls to
`log_start()` without `log_stop()` orphan Manager processes.

### 6. Solver mutable state visible across processes — `solver/solverpy.py:22–25`, `solver/solver.py:92`
`_exitcode` and `_output` are set on the solver during `solve()`. With spawn-based
multiprocessing, each worker gets its own copy so mutations are silently lost. Parent
never sees the exit code from the subprocess.

### 7. Talker log queue never started — `task/launcher.py:48–56`
`LogTalker` does not call `log_start()` before `launching()`, so `_log_queue` is always
`None`. Tasks receive a `None` logqueue and child process logging is never redirected —
all log output from workers is silently dropped.

### 8. Unreachable `raise` in `redirect.call()` — `tools/redirect.py:73`
`raise` after an `except` block that already unconditionally re-raises. Dead code that
suggests `KeyboardInterrupt` was meant to be handled separately (see commented-out code
nearby) but was never wired up.

---

## Medium

### 9. `Limits.__lt__` returns `None` — `solver/plugins/shell/limits.py:64–65`
Returns `None` (not `False`) when limits are incomparable. Python's sort/comparison
infrastructure expects `bool` from `__lt__`; `None` causes silent incorrect comparisons
or `TypeError` depending on context. See the existing `-> bool | None` annotation which
documents the problem but doesn't fix it.

### 10. `print()` inside `Limits.__init__` — `solver/plugins/shell/limits.py:43`
`print(e)` before re-raising bypasses the logging system. In multiprocessing workers
the output goes to the worker's stdout and is typically invisible. Use `logger.warning`.

### 11. LogTalker wait timers grow without bound — `task/logtalker.py:106,112`
`_wait_time *= 1.1` and `_wait_total *= 2` grow indefinitely. For runs of several hours
the logging interval becomes so large that hangs are effectively invisible.

### 12. Exception handling swallows pickling errors — `task/task.py:115–125`
`runtask` catches `Exception` but pickling failures in spawn mode are raised by the
Pool machinery **before** `runtask` runs, so they bubble up as opaque worker crashes
rather than useful error messages.

---

## Low / Design

### 13. Scheduler state not reset between loop iterations — `setups/loop.py`
`LogTalker`/`SolverTalker` instances created once and reused across loop iterations.
Their internal counters (`_solved`, `_unsolved`, `_errors`) are only reset per job, not
per iteration, which can give misleading progress totals in multi-loop runs.

### 14. Plugin order dependency implicit — `solver/pluginsolver.py:130–141`
`update()` then `finished()` is called on all decorators in sequence. Plugins that
depend on result state set by an earlier plugin's `update()` are fragile to reordering.
No documentation of expected order.

### 15. `mutable default` in `ShellSolver.__init__` / `StdinSolver.__init__`
`builder: "LimitBuilder" = {}` and `plugins: list["Plugin"] = []` are mutable defaults.
Same class of bug as issue #2 — safe only because these happen to not be mutated
in-place, but fragile.
