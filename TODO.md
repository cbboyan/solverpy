# TODO

Outstanding work for `solverpy` and `solverpy-learn`, ordered by importance
within each section. Headings use stable descriptive labels instead of numbers.

## Bugs

### tunerfailure

`prettytuner()` joins the tuner child without checking its exit code, and the
shared talker's result is not reset before a new run. A failed later tuner can
therefore return a stale result from an earlier run and select an old model.

Reset the result before launch, propagate abnormal child exits, and test that a
failed tuner cannot return stale state.

Relevant code:
`packages/solverpy-learn/src/solverpy_learn/builder/autotune/autotune.py`.

### solvedby

`solvedby` is intended only to accelerate the first real train/development
evaluation that recreates training data. The tuning setup inherits `solvedby`
and `it == 0`, so ATP evaluations during tuning are restricted to the
reference-solved subset and skipped problems become synthetic `TIMEOUT`
results. This biases model selection toward retaining reference solutions.

Apply `solvedby` only to the first real loop evaluation. Tuning evaluations
must always use their complete configured benchmark. Add a regression test.

Relevant code:
`packages/solverpy/src/solverpy/benchmark/evaluation.py` and
`packages/solverpy-learn/src/solverpy_learn/builder/autotune/build.py`.

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
