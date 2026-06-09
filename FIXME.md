# SolverPy Process and Lifecycle Issues

Review notes for `solverpy` and `solverpy-learn`. Address these one by one.
Preserve the intentional multiprocessing context split unless an individual fix
has a clear reason to change it.

## Process Context Constraints

- Evaluation pools normally use `forkserver` to avoid inheriting large ML,
  NumPy, OpenBLAS, and OpenMP state.
- ATP evaluation inside tuning uses `spawn` so workers do not inherit loaded
  training matrices.
- Training data is loaded inside the forked tuner process, not the main process.
  This prevents matrices from accumulating in the long-lived loop process.
- SVM chunk loading and compression use `fork` so temporary memory is reclaimed
  when the worker processes exit.
- The main problems are process ownership and shutdown, not the basic context
  choices.

## Critical

### 1. Pool workers ignored SIGINT - resolved 2026-06-09

- Removed the worker-side `signal.signal(SIGINT, SIG_IGN)`.
- `KeyboardInterrupt` now propagates naturally because it is not caught by
  `except Exception`.
- The main process still terminates and joins the evaluation pool.
- Solver shell/binary descendants can still briefly outlive terminated workers,
  but their configured short time limits make this acceptable for now.

### 2. Training plugins created unmanaged Manager servers - resolved 2026-06-09

- Training collectors now defer creation of shared locks and namespaces until
  the learning session starts.
- `solverpy_learn.setups.loop.initialize()` creates one forkserver Manager and
  connects all train/development collectors to it.
- Plugins store only Manager proxies, so Manager ownership is not serialized
  into evaluation workers.
- `Runtime.shutdown()` copies statistics back to local state, disconnects the
  proxies, and explicitly shuts down the Manager in `launch()`'s `finally`.
- A real process probe confirmed one Manager for two collectors and no remaining
  Manager after shutdown.

## High

### 3. Autotuner interruption kills only its direct child

- `packages/solverpy-learn/src/solverpy_learn/builder/autotune/autotune.py:150`
  calls `p.terminate()` but does not subsequently join it or terminate its
  descendants.
- The tuner may own spawn evaluation pools, fork data-loading pools, Manager
  connections, and solver subprocesses.
- This compounds the orphaning problem and likely contributes to requiring
  repeated `Ctrl+C`.

### 4. Tuner child failure is silently accepted

- `prettytuner()` joins the child but does not check `p.exitcode`.
- The shared talker's `_result` is not reset before a new tuning run.
- A failed later tuner can therefore return a stale result from an earlier run,
  potentially causing an old model to be selected or copied.
- Relevant code:
  `packages/solverpy-learn/src/solverpy_learn/builder/autotune/autotune.py:148`

### 5. Autotuner forks after starting threads

- `remote.listening_start()` starts a `QueueListener` and a remote-listener
  thread before the forked tuner process is started.
- Forking a multithreaded process can inherit locked logging or runtime state
  and cause intermittent deadlocks.
- Relevant code:
  `packages/solverpy-learn/src/solverpy_learn/builder/autotune/autotune.py:145`

### 6. The `external` decorator has no interrupt cleanup

- `packages/solverpy/src/solverpy/tools/external.py:22` starts a forked process
  and performs an unguarded `join()`.
- `KeyboardInterrupt` can leave that process, and potentially its pool children,
  running.
- This affects training-data compression.

## Medium

### 7. Same-file train/test constructs two LightGBM datasets

- When `f_test == f_train`, the sparse matrices are shared, but two separately
  constructed LightGBM `Dataset` objects are created.
- This likely duplicates native binned dataset memory and substantially raises
  peak memory.
- It should not accumulate across loops because the tuner is a separate process.
- Relevant code:
  `packages/solverpy-learn/src/solverpy_learn/builder/autotune/autotune.py:66`

### 8. Default RemoteTalker Manager is not shut down

- `packages/solverpy/src/solverpy/report/talker/remotetalker.py:88` creates an
  optional `_remote_manager`.
- `listening_stop()` never shuts that Manager down.
- Current autotuning passes a plain queue, but other default API usage can leak
  a Manager server.

### 9. Tests and root README use obsolete setup keys

- Production code expects `benchmarks` and `strategies`.
- `tests/test_benchmark_eval.py` and the root `README.md` still use `bidlist`
  and `sidlist`.
- Focused testing produced 128 passes and 21 setup errors caused by this
  mismatch.

## Missing Tests

- One `SIGINT` stops an evaluation promptly.
- Solver shell and binary descendants are gone after interruption.
- Tuner process and all nested pools are gone after interruption.
- Manager server count does not grow across loop iterations. Basic shared
  Manager creation/shutdown is covered; a full multi-iteration process-count
  test is still desirable.
- Failed tuner exits are propagated and cannot return stale results.
- `external` child processes are terminated and joined on interruption.
- Tests exercise `fork`, `forkserver`, and `spawn` paths explicitly.

## Development Environment

The active packages in `~/.local/lib/python3.14/site-packages` are symlinks into
this repository:

- `solverpy` -> `packages/solverpy/src/solverpy`
- `solverpy_learn` -> `packages/solverpy-learn/src/solverpy_learn`
- `solverpy_grackle` -> `packages/solverpy-grackle/src/solverpy_grackle`

Source updates are immediately active. Reinstallation is not required.
