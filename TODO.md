# Known Issues

## High

### 1. Refactor tuning pipeline to use `RemoteTalker` — `builder/autotune/autotune.py`

The current `LoopTalker` bakes a cross-process proxy directly into the talker via
`__getattribute__` intercepting a `REMOTES` set and routing calls to a
`multiprocessing.Queue`. This causes a freeze: the parent also goes through the same
`__getattribute__` override, piling eval events into the queue with nobody reading them.
The pipe buffer fills, the feeder thread blocks, and the forked child cannot exit.

**Plan:**
- Strip the `__getattribute__` / REMOTES proxy out of `LoopTalker` entirely. Talkers are
  pure UI components that always run in the main process.
- In `prettytuner()`, before forking, create `RemoteTalker(talker)` wrapping the real
  talker. Set `builder._devels["talker"] = remote` so ATP eval inside `build.score()`
  also routes through the single queue.
- The forked child calls methods on `remote`; `RemoteTalker`'s listening thread in the
  parent dispatches them to the real talker. One queue, no overflow.
- `tuner()` calls `talker.result(ret)` at the end; `RemoteTalker` forwards it to the
  real talker which stores the value (e.g. `self._result = val`).
- `prettytuner()` does `p.join()` then `remote.listening_stop()`. `listening_stop()`
  drains the queue fully before stopping the thread, so `result()` is guaranteed
  dispatched. The caller reads the stored value off the real talker directly — no
  `wait()` needed, no event signaling.
- `listening_start()` / `listening_stop()` remain on `RemoteTalker` only, with their
  original meaning (log queue + dispatch thread). Regular talkers never need them.

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
