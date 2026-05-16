# Known Issues

## High

### 1. Nested multiprocessing pools — `builder/autotune/build.py:157` + `task/launcher.py:51`
Root cause of the quadratic process issue. `build.score()` calls `evaluation.launch()`
→ `launcher.launch()` which opens a new `Pool(cores)`. If this runs inside a worker of
an outer pool (e.g. during Optuna trial evaluation), every outer worker spawns another
`cores` processes. Switching to `spawn` doesn't prevent this — it only changes how
processes are forked. The fix is to detect when already inside a worker (e.g. via a
global flag or env var) and run tasks sequentially instead of spawning a new pool.

Note: the related symptom of ~128 idle threads per evaluation worker (observed via
`pstree`) was a separate issue — numpy/scipy/sklearn module-level imports in
`builder/svm.py` were triggering OpenBLAS+OpenMP thread pool init in every spawn
worker at unpickle time. Fixed by making those imports lazy (see DONE.md).

### 2. Solver mutable state visible across processes — `solver/solverpy.py:22–25`, `solver/solver.py:92`
`_exitcode` and `_output` are set on the solver during `solve()`. With spawn-based
multiprocessing, each worker gets its own copy so mutations are silently lost. Parent
never sees the exit code from the subprocess.

### 3. Talker log queue never started — `task/launcher.py:48–56`
`LogTalker` does not call `log_start()` before `launching()`, so `_log_queue` is always
`None`. Tasks receive a `None` logqueue and child process logging is never redirected —
all log output from workers is silently dropped.

Related: in `RemoteTalker`, `log_start` is listed in `REMOTES`, so calling
`self.log_start()` from `listening_start()` queues the call to the local talker instead
of executing it. This means `_log_queue` is never set on the `RemoteTalker` instance,
and the `log_config` call in `autotune.tuner()` (which checks `builder.talker._log_queue`)
is never reached — child process logging is silently suppressed there too.

Note: this suppression in `prettytuner` may be intentional. The child runs LightGBM,
Optuna, and other noisy packages whose internal log output would pollute the log file.
Progress information from the child is already routed to the parent via the autotune
queue (messages like `"status"`, `"tried"`, `"trialed"`) and logged there by
`AutotuneListener` — so meaningful output reaches the log without opening the Python
logging channel from the child at all.

This reflects a generational design: the structured autotune queue messages came first
and are still the right mechanism for rich progress reporting (trial tables, scores,
etc.). The log queue was added later as a general-purpose channel. A future unification
could route all child logging through the log queue, but the message protocol is
non-trivial to replace and the two mechanisms serve somewhat different purposes.

### 4. Unreachable `raise` in `redirect.call()` — `tools/redirect.py:73`
`raise` after an `except` block that already unconditionally re-raises. Dead code that
suggests `KeyboardInterrupt` was meant to be handled separately (see commented-out code
nearby) but was never wired up.

## Medium

### 5. `Limits.__lt__` returns `None` — `solver/plugins/shell/limits.py:64–65`
Returns `None` (not `False`) when limits are incomparable. Python's sort/comparison
infrastructure expects `bool` from `__lt__`; `None` causes silent incorrect comparisons
or `TypeError` depending on context. See the existing `-> bool | None` annotation which
documents the problem but doesn't fix it.

### 6. `print()` inside `Limits.__init__` — `solver/plugins/shell/limits.py:43`
`print(e)` before re-raising bypasses the logging system. In multiprocessing workers
the output goes to the worker's stdout and is typically invisible. Use `logger.warning`.

### 7. LogTalker wait timers grow without bound — `task/logtalker.py:106,112`
`_wait_time *= 1.1` and `_wait_total *= 2` grow indefinitely. For runs of several hours
the logging interval becomes so large that hangs are effectively invisible.

### 8. Exception handling swallows pickling errors — `task/task.py:115–125`
`runtask` catches `Exception` but pickling failures in spawn mode are raised by the
Pool machinery **before** `runtask` runs, so they bubble up as opaque worker crashes
rather than useful error messages.

## Low / Design

### 12. RemoteTalker queue and Manager lifetime — `task/remotetalker.py:78–79`
Two issues:
1. `manager` is a local variable in `__init__` and goes out of scope immediately after;
   the Manager server process may be garbage-collected, invalidating the queue proxy.
   Fix: store as `self._manager` and shut it down in `terminate()`/`log_stop()`.
2. `RemoteTalker` always creates a forkserver Manager queue, even when the consumer is
   a forked child (e.g. `prettytuner`). A plain `fork`-context `Queue` would suffice there.
   Fix: accept an optional `queue` argument; if provided, use it directly; otherwise
   fall back to creating the Manager queue (default behavior, for forkserver workers).


### 9. Scheduler state not reset between loop iterations — `setups/loop.py`
`LogTalker`/`SolverTalker` instances created once and reused across loop iterations.
Their internal counters (`_solved`, `_unsolved`, `_errors`) are only reset per job, not
per iteration, which can give misleading progress totals in multi-loop runs.

### 10. Plugin order dependency implicit — `solver/pluginsolver.py:130–141`
`update()` then `finished()` is called on all decorators in sequence. Plugins that
depend on result state set by an earlier plugin's `update()` are fragile to reordering.
No documentation of expected order.

### 11. Mutable defaults in `ShellSolver.__init__` / `StdinSolver.__init__`
`builder: "LimitBuilder" = {}` and `plugins: list["Plugin"] = []` are mutable defaults.
Same class of bug as the fixed `SolverTask` issue — safe only because these happen to
not be mutated in-place, but fragile.

# Backlog

1. automated restriction to solvable problems (force implementation)
2. trains regeneration
3. show best iteration in the training report
4. show the initial model in the report
5. reporting: graphs, super-fences (e.g. render graph data → SVG); `solverpy report` HTML conversion done, superfences not yet wired
6. progress web api
7. improve total bar ETA by not including skipped problems
8. improve ETA by considering timeout
9. nice ntfy messages
10. solverpy command script (unified CLI, Approach A) — mostly done
   - core subcommands: `init` ✓, `run` ✓, `clean` ✓, `esid2strat` ✓, `report` ✓
   - stubs remaining: `eval sid bid`, `loop bid-train bid-devel`
   - learn subcommands: `tune` ✓, `compress` ✓, `decompress` ✓, `deconflict` ✓, `filter` ✓
   - remaining: remove old `scripts/` shell scripts once stubs are implemented
11. yaml formatter: use named globals (like `trains:`) instead of YAML anchors `&id001`
    (tried `_shared`/`_replace` approach — reverted; setup+devels now combined in one block)
12. scripts update
13. simulated runs from previous outputs
14. tuning phase for posneg balancing - requires full data storage
