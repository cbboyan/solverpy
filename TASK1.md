# TASK1: Experiment Setup Refactor

## Goal

Make `experiment()` the real session entry point. After `experiment(setup)`,
the setup should be normalized and contain the stable session-level keys that
later setup functions can rely on. Logging, reporting, runtime ownership, and
the talker should exist from the beginning of the experiment, while solver and
training plugins can still be added afterward.

Target user-facing flows:

```python
# plain evaluation
from solverpy import setups

setups.experiment(setup)
setups.eprover(setup)
setups.launch(setup)
```

```python
# ML / ENIGMA
from solverpy_learn import setups

setups.experiment(setup)
setups.eprover(setup)
setups.enigma(setup)
setups.launch(setup)
```

Eventually, builder helpers may also become convenience orchestrators:

```python
setups.experiment(setup)
setups.enigma(setup)   # may call the appropriate solver setup itself
setups.launch(setup)
```

## Current Shape

The setup lifecycle is split across several functions:

- `solverpy.setups.loop.experiment()` only normalizes `common`, `evals`, and
  the legacy `trains` alias into `Evalset` objects.
- `solverpy.setups.common.init()` is called from solver setup functions and
  fills defaults such as `options`, `limit`, `dataname`, and base DB/output
  plugins.
- `solverpy.setups.loop.evaluation()` fills evaluation defaults:
  `cores`, `delfix`, `db`, `ntfy`, `ref`, strategies, benchmarks, and id
  validation.
- `benchmark.evaluation.init()` initializes logging/reporting and writes the
  setup section into the report. It is currently called from `launch()`.
- `solverpy.setups.loop.boot()` creates `EvalTalker`, creates `Runtime`,
  attaches `runtime.log_queue` to the talker, starts talker log forwarding,
  and stores `setup["talker"]`.
- `solverpy_learn.setups.loop.boot()` duplicates the same shape but chooses
  `LoopTalker` when `loops` is present.

The runtime currently constructs a forkserver `Manager` and immediately calls
`connect(manager)` on every managed plugin already present in the setup.
That is too early for the desired flow because `experiment()` runs before
solver setup creates evalset-local plugins such as ENIGMA/cvc5 train collectors.

## Design

### 1. Move Common Session Bootstrap Out Of `loop.py`

Create a shared helper module, preferably `solverpy.setups.experiment` or
expanded `solverpy.setups.common`, with small composable functions:

- `evalsets_normalize(setup)`: current `experiment()` logic for `common`,
  `evals`, `devels`, and `trains`.
- `defaults_setup(setup)`: current `common.init()` session defaults plus
  evaluation defaults that do not require a solver.
- `logging_setup(setup, name=None)`: current `benchmark.evaluation.init()`
  responsibilities, or a renamed lower-level helper, so logging/reporting
  happens during `experiment()`.
- `runtime_create(setup)`: create a runtime manager and log queue, but do not
  require all plugins to exist yet.
- `talker_create(setup, talker_factory)`: create the right talker, attach the
  runtime log queue, start log forwarding, and store `setup["talker"]`.
- `runtime_connect(setup)`: connect all managed plugins present in
  `setup["plugins"]`, `evals["plugins"]`, and `devels["plugins"]`.

The public `solverpy.setups.experiment()` should call these shared helpers with
`EvalTalker`. The public `solverpy_learn.setups.experiment()` should call the
same helpers with `LoopTalker`/`EvalTalker` selection.

This keeps the unavoidable difference between `solverpy` and `solverpy-learn`
to a talker factory instead of duplicating the full experiment setup.

### 2. Split Runtime Manager Creation From Plugin Connection

Refactor `Runtime` so it owns the manager immediately but can connect managed
plugins later:

```python
runtime = Runtime()
runtime.log_queue
runtime.plugins_connect(plugins)
runtime.shutdown()
```

Important behavior:

- `Runtime.__init__()` creates the forkserver manager and `log_queue`.
- `Runtime.plugins_connect(plugins)` deduplicates by object identity and
  connects only plugins not already connected by this runtime.
- `Runtime.shutdown()` disconnects all connected plugins and shuts down the
  manager.
- The existing `initialize(setup)` can remain as a compatibility wrapper that
  creates a `Runtime` and immediately connects current plugins, but new code
  should use the split lifecycle.

This is safer than trying to connect plugins during solver setup because all
solver setup functions can remain focused on constructing solvers/plugins.
`launch()` becomes the single point that says: "all plugins should now exist;
connect them before evaluation starts."

Do not remove `connect()` entirely yet. Train plugins currently rely on their
manager-backed locks/namespaces before multiprocessing evaluation. Keeping an
explicit connection phase preserves that invariant.

### 3. Fold `evaluation()` Into `experiment()`

Move most of `solverpy.setups.loop.evaluation()` into the new experiment
bootstrap:

- `cores`
- `delfix`
- `db`
- `ntfy`
- per-evalset `ref`
- loading `sidfile`/`bidfile`
- validating strategy and benchmark ids

One practical issue: validation can run before solver setup, but it should run
after evalsets exist. That matches `experiment()`.

Another practical issue: solver setup currently may create default evalsets in
some learning paths, especially `solverpy_learn.setups.cvc5(setup, key=...)`.
The preferred direction should be: user-facing flows create `evals` before
solver setup; internal convenience helpers that create evalsets should also
call the shared evalset default/validation helper before launch.

Keep `setups.evaluation(setup)` as a compatibility alias initially. It should
be idempotent and delegate to the shared helper, but the new documented flow
should omit it.

### 4. Move `common.init()` Defaults Into `experiment()`

Session-level defaults should be available immediately after `experiment()`:

- `options`, including ensured `flatten` and `compress` decisions
- `limit`
- `dataname`
- `plugins`

Solver setup functions should stop calling `common.init()` as a hidden
side-effect once the migration is complete. During migration, `common.init()`
can remain idempotent and call the shared default helper so old flows keep
working.

Be careful with plugin defaults:

- Base DB/output/proof plugins can be created during `experiment()`.
- Solver-specific replacements such as `EProverSid()` should remain in the
  solver setup, because only the solver setup knows it is configuring E.
- Training plugins remain in solver setup because they depend on ENIGMA/cvc5
  training configuration.

### 5. Make `launch()` Mostly Connect And Run

After the refactor, base `solverpy.setups.launch()` should do roughly:

1. Ensure `experiment()` has run, or call it lazily for backward compatibility.
2. Ensure solver/evalset requirements exist (`evals`, `solver`, benchmarks,
   strategies, talker, runtime).
3. Connect runtime to all current managed plugins.
4. Send init notification.
5. Launch benchmark evaluation.
6. Send done notification.
7. Stop talker logging and shut down runtime.

The learning `launch()` should share the same runtime/talker shutdown logic,
then keep its loop-specific iteration behavior.

The current `boot()` functions should disappear or become private thin wrappers
during migration. Their current responsibilities belong to `experiment()` plus
`runtime_connect()`.

### 6. Talker Selection

Add a shared public or private helper that accepts a factory:

```python
def experiment_bootstrap(setup, talker_make):
   ...
   setup["talker"] = talker_make(setup)
```

Base package:

```python
def talker_eval(setup):
   return EvalTalker(headless="headless" in setup["options"])
```

Learning package:

```python
def talker_learn(setup):
   cls = LoopTalker if "loops" in setup else EvalTalker
   return cls(headless="headless" in setup["options"])
```

This avoids a hard dependency from `solverpy` to `solverpy_learn`, keeps the
two public `experiment()` functions unavoidable but tiny, and avoids duplicating
logging/runtime/default setup.

### 7. Builder Convenience

After the core lifecycle is stable, add optional convenience behavior:

- `solverpy_learn.setups.enigma(setup, ...)` may call `eprover(setup)` if
  no evalset solver/plugin has been configured yet.
- `solverpy_learn.setups.cvc5ml(setup, ...)` may call `cvc5(setup)` if
  no evalset solver/plugin has been configured yet.

Do this only after making the explicit flow work cleanly:

```python
experiment -> eprover/cvc5 -> enigma/cvc5ml -> launch
```

The convenience call should be conservative:

- If solvers/plugins already exist, do not rebuild them.
- If ENIGMA features are missing, fail with a clear error before calling
  `eprover`.
- Keep solver choice explicit when ambiguity would be surprising.

## Migration Steps

1. Add the shared experiment helper module.
2. Refactor `Runtime` into manager creation plus later plugin connection.
3. Change base `solverpy.setups.experiment()` to perform normalization,
   defaults, logging/report setup, runtime creation, and `EvalTalker` creation.
4. Add `solverpy_learn.setups.experiment()` that delegates to the shared helper
   with learning talker selection.
5. Make `launch()` call `runtime_connect(setup)` instead of `boot()`.
6. Make `setups.evaluation()` an idempotent compatibility wrapper and remove it
   from CLI/documented examples.
7. Update solver setup functions so hidden `common.init()` calls are no longer
   necessary in the new flow, while preserving old-flow compatibility for now.
8. Add builder convenience (`enigma()` calls `eprover()`, `cvc5ml()` calls
   `cvc5()`) only after tests cover the explicit flow.
9. Update docs and YAML runner flows:
   - evaluation YAML: `experiment -> solver -> launch`
   - loop YAML: `experiment -> solver -> builder -> launch`
10. Later cleanup: remove or deprecate `boot()` and the old public
    `evaluation()` step once downstream users have migrated.

## Tests To Add Or Update

- Base experiment bootstrap:
  - `setups.experiment(setup)` creates `options`, `db`, `ntfy`, `runtime`,
    `talker`, and normalized `evals`.
  - It initializes logging/reporting once and is idempotent enough for repeated
    guarded calls.
  - It does not require solver plugins to exist.

- Base new flow:
  - `experiment -> eprover -> launch` works without `evaluation()`.
  - Existing `experiment -> eprover -> evaluation -> launch` still works.

- Learning new flow:
  - `experiment -> eprover -> enigma -> launch` works without `evaluation()`.
  - `experiment -> cvc5 -> cvc5ml -> launch` works without `evaluation()`.
  - `solverpy_learn.setups.experiment()` chooses `LoopTalker` when `loops`
    exists and `EvalTalker` otherwise.

- Runtime split:
  - Runtime can be created before plugins.
  - Plugins created after experiment are connected by launch.
  - Connected managed plugins are disconnected on normal completion and failure.
  - Repeated connection does not reconnect the same plugin object twice.

- Compatibility:
  - Old CLI/YAML paths continue to run while `evaluation()` remains.
  - `common.init()` remains safe if called by legacy solver setup paths.

## Risks And Open Questions

- Logging initialization is currently global and one-shot. Moving it earlier is
  fine, but tests that monkeypatch logging/reporting need to account for the
  global `_logfile` guard.
- `benchmark.evaluation.init()` currently both initializes logging and writes
  the setup report. After moving it, the report should capture the setup after
  experiment defaults, but possibly before solver setup adds solver objects.
  Decide whether to write a second "resolved setup" section at launch or delay
  report emission until after solver setup while still initializing logging in
  experiment.
- Validation during `experiment()` may read `sids`/`bids` before solver setup.
  That is probably correct, but compatibility wrappers should handle evalsets
  added later by helper functions.
- `Runtime` owns a multiprocessing Manager. Creating it in `experiment()` means
  sessions that never call `launch()` still own a Manager unless callers clean
  up. Consider a context-manager API or `setup["runtime"].shutdown()` guidance.
- If `experiment()` creates the talker and starts log forwarding, a failed
  solver setup must still shut it down. This argues for a public
  `setups.close(setup)` or making `launch()` the owner only after successful
  experiment setup.

## Expected End State

The setup API becomes easier to explain:

- `experiment()` creates the session.
- solver setup chooses how to solve and which plugins collect data.
- builder setup chooses what model to build.
- `launch()` connects plugins and runs.

The only package-specific duplication is the public `experiment()` wrapper that
selects the correct talker. The shared lifecycle code lives in `solverpy`, and
`solverpy-learn` supplies only the learning talker factory and ML-specific
solver/builder setup.
