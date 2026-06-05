# Known Issues

## High

### 1. Refactor tuning pipeline to use `RemoteTalker` — `builder/autotune/autotune.py`

**✓ Subtask 1a done:** `RemoteTalker` revival — proxy machinery stripped from `TuneTalker`;
`prettytuner()` wraps the real talker in `RemoteTalker(talker, queue=multiprocessing.Queue())`,
forks the child with `remote` as the talker, does `p.join()` then `remote.listening_stop()`
(which drains the queue to guarantee `tune_result` is dispatched), and returns `talker._result`.
`RemoteTalker` uses a `LOCALS` set (inverse of the old `REMOTES`): every public method not
in `LOCALS` is queued; `LOCALS` contains only `log_*`, `listening_*`, and `listening_handle`.
`_local` is excluded from pickling so spawn workers only carry the queue.
`Talker` now defines no-op stubs for all tuning/build methods so `Talker | None` is the
correct type throughout `tune.py`, `check.py`, `build.py`, and `autotune.py`.

---

**Subtask 1b: Logging refactor — route child and worker logging through the queue**

Goal: all Python `logging` records from the child (tuner) process and from ATP spawn
workers travel through the log queue to the parent's handlers.  Child stdout/stderr
(LightGBM output) continues to be captured by `redirect.call` into `autotune.log`.

Files: `autotune/autotune.py`, `report/talker/remotetalker.py`, `report/talker/talker.py`

- `prettytuner()` already calls `remote.listening_start()` which calls `super().listening_start()`
  → `log_start()`, creating a forkserver Manager queue at `remote._log_queue` and starting
  the `QueueListener` in the parent.  Since the child is forked *after* this, it inherits
  the queue object.
- After `remote.listening_start()`, set `talker._log_queue = remote._log_queue` so that
  when `eval_launch` is dispatched to `TuneTalker`, it injects the queue into ATP spawn
  worker tasks (the existing `Talker.eval_launch` already does this if `_log_queue` is
  set).
- Pass `logqueue=remote._log_queue` to the child via `kwargs` (or read it from the
  forked `remote` object), and call `Talker.log_config(logqueue)` at the top of `tuner()`
  to redirect the child's root logger through the queue.
- After this change: child `logger.*` calls → `QueueHandler` → pipe → parent
  `QueueListener` → parent handlers (console / file).  ATP worker `logger.*` calls →
  same path (injected via `eval_launch`).  LightGBM stdout → `redirect.call` fd
  redirect → `autotune.log` (unchanged).
- `Talker.listening_start()` currently always calls `log_start()` (forkserver Manager).
  Consider whether a plain `multiprocessing.Queue` is sufficient here too (avoids a
  forkserver process), or keep the Manager for picklability into spawn workers.

---

**Subtask 1c: Move child-side logging to talker methods**

Goal: remove scattered `logger.debug/info` calls from child-process code (`tuner()`,
`build.py`, `tune.py`, `check.py`) and replace them with `talker.info/debug` calls or
new talker events.  After 1b these calls already reach the parent via the queue, but
routing through the talker makes the interface explicit and avoids depending on the log
queue being set up correctly.

Files: `autotune/autotune.py`, `autotune/build.py`

- `tuner()`: replace `logger.debug(f"posneg balancing: ...")` with `talker.debug(...)`.
  Replace `logger.debug("- initial model: ...")` with `talker.debug(...)` or fold into
  the existing `build_done` / `tune_trial_done` flow.
- `build.py`: the `report("debug", ...)` calls already go through the talker.  Any
  remaining bare `logger.*` calls in the child path should become `talker.debug/info`.
- After both 1b and 1c, `talker.info/debug` in `LogTalker` can be promoted from no-ops
  to real `logger.info/debug` calls in the parent, replacing the current `info()`/`debug()`
  stubs in `Talker`.
- ATP spawn workers (`task/task.py`, `task/runtask.py`) should have no direct logging;
  all their log records are already captured by the worker's own root logger which will
  route through the injected queue after subtask 1b.

---

### 1d. Refactor Talker hierarchy to multiple inheritance — `report/talker/`

After subtasks 1a–1c, the `TuneTalker` is a pure UI class inheriting a long chain
`Talker → LogTalker → SolverTalker → TuneTalker`.  Refactor to composable mixins.

**Proposed structure:**

```
Talker                  — abstract base: all lifecycle hooks as no-ops
  EvalTalker            — log-based eval methods (begin/end/next/launching/finished/done/status)
  TuneEventTalker       — log-based tune methods (trials/trying/tried/trialed/building/iteration/built/tuning/tuned/result)
  EvalBarTalker(Talker) — bar overrides for eval events; owns _total_bar / _task_bar slots
  TuneBarTalker(Talker) — bar overrides for tune events; shares _total_bar / _task_bar slots
  RemoteTalker          — cross-process proxy (unchanged)

# Concrete classes (via MI):
SolverTalker(EvalBarTalker, EvalTalker)                         — solverpy (eval only)
FullTalker(EvalBarTalker, TuneBarTalker, EvalTalker, TuneEventTalker) — solverpy-learn (eval + tuning)
```

**Bar model:** exactly two slots, `_total_bar` and `_task_bar`, defined on a shared
`BarTalker` base (slots only, no logic). The assigned bar type changes by context:

| Context | `_total_bar` | `_task_bar` |
|---|---|---|
| Normal eval | `RunningBar` | `SolvingBar` |
| Tuning (eval phase) | `DefaultBar` (trial counter) | `RunningBar` (leave=False) |
| Tuning (build phase) | `DefaultBar` (trial counter) | `BuilderBar` |

**Handler pattern:** store a callable alongside each bar at creation time so callers
never need to know the bar type:

```python
self._task_bar = BuilderBar(...)
self._task_update = lambda v: self._task_bar.status(v)
# finished() and iteration() both call self._task_update(v)
```

**New events:** add `tune_eval_begin(jobs)` and `tune_eval_end(results)` called from
`prettytuner()` to bracket the ATP evaluation phase inside tuning. This lets
`EvalBarTalker` distinguish "create normal eval bars" from "create inner eval bar
(leave=False)" without overriding `eval_begin`/`eval_end` with `report=False` hacks.

## Medium

### 2. `Limits.__lt__` returns `None` — `solver/plugins/shell/limits.py:64–65`
Returns `None` (not `False`) when limits are incomparable. Python's sort/comparison
infrastructure expects `bool` from `__lt__`; `None` causes silent incorrect comparisons
or `TypeError` depending on context. See the existing `-> bool | None` annotation which
documents the problem but doesn't fix it.

### 3. `print()` inside `Limits.__init__` — `solver/plugins/shell/limits.py:43`
`print(e)` before re-raising bypasses the logging system. In multiprocessing workers
the output goes to the worker's stdout and is typically invisible. Use `logger.warning`.

### 4. LogTalker wait timers grow without bound — `task/logtalker.py:106,112`
`_wait_time *= 1.1` and `_wait_total *= 2` grow indefinitely. For runs of several hours
the logging interval becomes so large that hangs are effectively invisible.

### 5. Exception handling swallows pickling errors — `task/task.py:115–125`
`runtask` catches `Exception` but pickling failures in spawn mode are raised by the
Pool machinery **before** `runtask` runs, so they bubble up as opaque worker crashes
rather than useful error messages.

## Low / Design

### 6. Unreachable `raise` in `redirect.call()` — `tools/redirect.py:73`
`raise` after an `except` block that already unconditionally re-raises. Dead code that
suggests `KeyboardInterrupt` was meant to be handled separately (see commented-out code
nearby) but was never wired up.

### 7. Solver mutable state visible across processes — `solver/solverpy.py:22–25`, `solver/solver.py:92`
`_exitcode` and `_output` are set on the solver during `solve()`. With spawn-based
multiprocessing, each worker gets its own copy so mutations are silently lost. These
values are process-internal and never needed in the parent, so this is by design.

### 9. Talker log queue never started — `task/launcher.py`
`LogTalker` does not call `log_start()` before `launching()`, so `_log_queue` is always
`None` and child process logging is never redirected to the parent. This is intentional:
worker log output is process-internal. To enable forwarding if ever needed: call
`log_start()` in `listening_start()` and inject `_log_queue` into tasks in `launching()`.

### 10. Scheduler state not reset between loop iterations — `setups/loop.py`
`LogTalker`/`SolverTalker` instances created once and reused across loop iterations.
Their internal counters (`_solved`, `_unsolved`, `_errors`) are only reset per job, not
per iteration, which can give misleading progress totals in multi-loop runs.

### 11. Plugin order dependency implicit — `solver/pluginsolver.py:130–141`
`update()` then `finished()` is called on all decorators in sequence. Plugins that
depend on result state set by an earlier plugin's `update()` are fragile to reordering.
No documentation of expected order.

### 12. Mutable defaults in `ShellSolver.__init__` / `StdinSolver.__init__`
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
