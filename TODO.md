# TODO

Outstanding work for `solverpy` and `solverpy-learn`, ordered by importance
within each section. Headings use stable descriptive labels instead of numbers.

## Refactors

### dataset

Extract a `Dataset` TypedDict from `Setup` to separate per-dataset fields from
shared experiment configuration.  Currently `Setup` holds everything and a
parallel `devels: Setup` argument is threaded through most functions.  After
this refactor `Setup` has two nested fields — `training: Dataset` and
`devels: Dataset` — and all functions that currently take a separate `devels`
argument drop it.

**New `Dataset` TypedDict** (new file `solverpy_learn/setups/dataset.py`):
```
benchmarks, strategies, refs, ref,
trains, dataname, basedataname, previous_trains,
proofs, max_proofs, start_dataname
```

**`Setup` changes**: remove all the above fields; add `training: Dataset` and
`devels: Dataset`.  `sel_features`, `gen_features` and other ML hyperparams
stay in `Setup` as shared config.

**Key mechanical changes** (all files listed relative to `packages/`):

1. `evaluation.py:init()` and all `launch(setup, devels=None)` signatures —
   drop the `devels` parameter; callers read `setup.get("devels")` instead.
   Affected: `solverpy/benchmark/evaluation.py`,
   `solverpy/setups/loop.py`, `solverpy_learn/setups/loop.py`.

2. `evaluator.launch(talker=talker, **setup)` at three call sites cannot
   spread `Setup` directly any more — dataset fields are nested.  Introduce a
   helper `eval_kwargs(setup: Setup, dataset: Dataset) -> dict` that merges
   shared fields with a given dataset (excluding the `training`/`devels` keys)
   and use it at every `**setup` spread:
   - `solverpy/setups/loop.py:60`
   - `solverpy_learn/setups/loop.py:167`
   - `solverpy_learn/builder/autotune/build.py:199`

3. `loopinit(setup)` and `looping(setup)` in `solverpy_learn/setups/loop.py`
   currently mutate dataset fields directly on `setup`.  Change them to take
   and return a `Dataset`, operating on `setup["training"]` (or the devels
   dataset) at the call site.

4. `oneloop(setup, talker, dataset)` in `solverpy_learn/setups/loop.py`
   operates on one dataset at a time.  Change signature to
   `oneloop(setup, dataset: Dataset, talker, label)` and update all field
   accesses (`trains`, `dataname`, `benchmarks`, `strategies`, etc.) to go
   through the `Dataset` argument instead of `setup`.

5. `initialize(setup, devels)` in `solverpy_learn/setups/loop.py` — collect
   trains from `setup["training"]` and `setup.get("devels")` instead of the
   two separate Setup arguments.

6. `do_loop` / `do_iter` closures in `launch()` — currently called with the
   full `setup` or `devels` Setup object; change them to call
   `oneloop(setup, setup["training"], ...)` and
   `oneloop(setup, setup["devels"], ...)`.

7. `AutoTuner.__init__` and all `EnigmaModel` / `EnigmaSel` / `EnigmaGen` /
   `Enigma` / `Cvc5ML` constructors — currently take `trains: Setup, devels:
   Setup`.  Change to take `setup: Setup`; access `setup["training"]` and
   `setup["devels"]` internally.  Store them as `self._training: Dataset` and
   `self._devels: Dataset`.  `self._dataname` comes from
   `setup["training"]["dataname"]`.

8. `EnigmaModel` — replace `self._fkey` / `self._trains[self._fkey]` with
   `self._features: str` initialised from `setup["sel_features"]` or
   `setup["gen_features"]` at construction time.

9. `autotune/build.py:score()` — replace
   `Setup(builder._devels, strategies=strategies)` with
   `eval_kwargs(setup, builder._devels | {"strategies": strategies})`.

10. `enigma.py` sub-builder construction (lines ~159–179) — copy patterns like
    `Setup(trains, trains=trains["trains"]._sel)` become
    `Dataset(trains_dataset, trains=trains_dataset["trains"]._sel)`.

11. `setups/solver.py` and `setups/tuner.py` — setup construction helpers
    that currently set `setup["trains"]`, `setup["dataname"]` etc. must
    instead build or update `setup["training"]`.

12. `scripts/run.py` and all tests that build Setup dicts directly — update to
    nest dataset fields under `setup["training"]` (and optionally `"devels"`).

**Risk areas**:
- `evaluation.run()` receives `it`, `proofs`, `max_proofs` via `**others`
  from the merged dict; after refactor these come from `Dataset` through
  `eval_kwargs`, so verify they still flow through.
- `loopinit()` / `looping()` mutate the dataset in-place; since `Dataset` is
  a plain dict nested inside `Setup`, mutations propagate correctly without
  special handling.
- `builder.reset(dataname)` is called with `dataset["dataname"]` after
  `loopinit` updates it; the call site in `loopinit` must use the dataset's
  updated value.
- `solvedby` field: currently popped in `build.py`; not declared in `Setup`;
  verify it is never set on the dataset side before removing.

## Bugs

### tunerfailure

`prettytuner()` joins the tuner child without checking its exit code, and the
shared talker's result is not reset before a new run. A failed later tuner can
therefore return a stale result from an earlier run and select an old model.

Reset the result before launch, propagate abnormal child exits, and test that a
failed tuner cannot return stale state.

Relevant code:
`packages/solverpy-learn/src/solverpy_learn/builder/autotune/autotune.py`.

### dbcache

`DB.loaded` retains every provider for every `(bid, sid)` pair for the lifetime
of the learning loop. Cached providers such as `Jsons` retain complete result
dictionaries, and `DB.commit()` revisits all historical providers. Experiments
with many generated strategies therefore grow the main process by roughly the
size of each loop's result data.

Define an evaluation-scoped provider lifetime or eviction mechanism. Providers
must be committed before release, while reuse within one evaluation should
remain cheap. Add a multi-loop memory/provider-count regression test.

Relevant code:
`packages/solverpy/src/solverpy/benchmark/db/db.py` and
`packages/solverpy/src/solverpy/benchmark/db/providers/jsons.py`.

### interrupts

The `external` decorator starts a forked process and performs an unguarded
`join()`. `KeyboardInterrupt` can leave that process and its pool descendants
running, notably during training-data compression.

Terminate and join the complete child process tree on interruption and test the
cleanup path.

Relevant code: `packages/solverpy/src/solverpy/tools/external.py`.

### terminationreporting

Experiment logs do not reliably record how a run ended. Normal completion and
user interruption should both emit an explicit final log message, and both
paths should send an `ntfy` notification with the termination reason. The
current learning-loop `KeyboardInterrupt` handler prints only
`Terminated (keyboard interrupt)` to the launching terminal, so the message is
not necessarily preserved in the experiment `.log`.

Make final reporting idempotent so each run emits exactly one terminal status,
including when nested tuner/evaluation cleanup also handles the interruption.
Cover normal completion and single-`Ctrl+C` shutdown in tests.

Relevant code:
`packages/solverpy-learn/src/solverpy_learn/setups/loop.py` and the setup/log
notification lifecycle.

### remotelifecycle

The default `RemoteTalker` constructor owns a forkserver `Manager`, but normal
listener shutdown does not shut that manager down. Current autotuning passes a
plain queue and is unaffected; default API users can leak a Manager server.

Make manager ownership explicit and shut it down idempotently. Test repeated
construction and shutdown.

Relevant code:
`packages/solverpy/src/solverpy/report/talker/remotetalker.py`.

### limits

`Limits.__lt__()` returns `None` for some incomparable limits. Python
comparison machinery expects a boolean, and cached-result simulation relies on
this ordering.

Define and test the intended partial-order behavior without returning `None`.

Relevant code:
`packages/solverpy/src/solverpy/solver/plugins/shell/limits.py`.

### limitlogging

`Limits.__init__()` prints parsing errors directly before raising. This
bypasses logging and is usually invisible in multiprocessing workers.

Report the invalid limit through logging or exception context instead.

### progress

`LogTalker` multiplies its time and task reporting intervals without a cap.
During long runs, progress messages can become too sparse to distinguish slow
work from a hang.

Cap or otherwise bound both reporting intervals.

Relevant code:
`packages/solverpy/src/solverpy/report/talker/logtalker.py`.

### nestedbarpadding

The outer tuning bar is shorter than its inner build/evaluation bar. When tqdm
redraws the outer bar after an inner evaluation update, characters from the
longer line can remain visible, for example `0/16998 !0` instead of `0/16`.

Pad nested bars to a shared visible line width. Extend the existing
`_postfix_width()`/`{pad}` mechanism to cover the complete suffix, including
the differing `n/total` widths, and have `LoopTalker` calculate the maximum
suffix width from the outer trial count and inner evaluation size. Avoid fixed
spaces and account for ANSI colour sequences. Add a formatting regression test
that redraws a tune bar after a longer evaluation bar and verifies that no
stale suffix remains.

Relevant code:
`packages/solverpy/src/solverpy/report/talker/bar.py` and
`packages/solverpy-learn/src/solverpy_learn/report/talker/looptalker.py`.

### pickling

`Task.runtask()` catches exceptions raised by task execution, but spawn-time
pickling failures occur in the pool before `runtask()` and surface as opaque
worker failures.

Add useful context at the pool submission/result boundary and cover the spawn
failure path.

### mutable

`ShellSolver`, `StdinSolver`, and `SolverPy` use mutable default dictionaries
or lists for constructor arguments. Current code concatenates rather than
mutating them, but the API remains fragile.

Replace the defaults with `None` and initialize per instance.

### redirect

`redirect.call()` has an unreachable `raise` after an exception handler that
already re-raises. Remove the dead code and clarify the intended
`KeyboardInterrupt` behavior.

## Features

### streaming

Construct LightGBM datasets incrementally from sparse NPZ chunks so only a
bounded number of chunks are resident at once. Preserve parallel chunk
processing and cheap link-based train-data merging.

The LightGBM C API supports sparse row insertion. A native LightGBM binary file
may be used as a derived cache, but should not replace the canonical chunked
data.

Also benchmark thread-based NPZ chunk loading. NumPy/SciPy decompression and
array work should release the GIL sufficiently, while threads avoid process
result serialization and the page-table cost of forking a process with a large
resident LightGBM dataset. Cap concurrency by the number of chunks regardless
of executor type. Keep `spawn` as a fallback to evaluate, not the default:
loaded sparse matrices would still need to be serialized back to the parent.

### talkers

Consider replacing the current `Talker -> LogTalker -> EvalTalker ->
LoopTalker` inheritance chain with composable evaluation and tuning mixins.
Keep the existing two-bar behavior and the current event API.

### solvable

Provide an explicit forced mode for restricting an evaluation to problems
known to be solvable. Keep this separate from the loop-internal `solvedby`
optimization described above.

### regeneration

Add an explicit workflow for regenerating training data rather than relying on
manual experiment setup changes.

### bestiteration

Show the selected LightGBM iteration in the training report.

### initialmodel

Show the initial model and its result in the tuning report.

### reporting

Extend reports with graphs and custom superfences, including rendering graph
data to SVG. Offline Markdown-to-HTML conversion already exists.

### webapi

Expose evaluation and tuning progress through a web API.

### eta

Improve progress ETA by excluding skipped problems and accounting for per-task
timeouts.

### notifications

Improve `ntfy` notification content.

### cli

Finish the unified command line interface. `init`, `run`, `clean`,
`esid2strat`, `report`, `tune`, `compress`, `decompress`, `deconflict`, and
`filter` exist; `eval` and `loop` remain stubs. Remove superseded shell scripts
after their replacements exist.

### yaml

Make setup YAML use named shared globals such as `trains` instead of generated
anchor names such as `&id001`.

### scripts

Update remaining experiment scripts to current setup and CLI APIs.

### replay

Support simulated runs reconstructed from previously saved solver outputs.

### plugins

Document or remove the implicit decorator ordering dependency: all `update()`
methods run before all `finished()` methods, and some plugins depend on state
created by an earlier plugin.

## Test Coverage

The related tasks above should add focused tests. Broader process coverage is
still needed for:

- evaluation interruption and solver descendant cleanup;
- tuner interruption and nested pool cleanup;
- repeated loop iterations without Manager or provider growth;
- explicit `fork`, `forkserver`, and `spawn` paths.
