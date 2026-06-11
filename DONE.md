# DONE

## Memory-efficient tuning accuracy and dataset reuse ✓

Autotuning no longer retains complete train/development CSR matrices alongside
LightGBM's native datasets.

- Datasets use `free_raw_data=True`; each CSR input is released immediately
  after native construction.
- Development data is constructed with the training dataset as its LightGBM
  reference, preserving compatible feature bins without retaining raw data.
- Dataset parameters are applied during construction. The `min_data` tuning
  phase sets `feature_pre_filter=false` before construction so later trials can
  change the threshold without rebuilding from raw data.
- When train and validation filenames are identical, one native dataset is
  reused. Validation statistics mirror training statistics and early stopping
  is disabled because there is no independent validation set.
- Threshold accuracy is vectorized and evaluated once on the selected native
  model iteration through LightGBM's custom evaluation API. The booster is
  rolled back to the selected iteration before evaluation and saving.
- `build_step()` now forwards labeled per-dataset metrics to the talker.
  `build_selected()` reports the selected iteration and its train/validation
  overall, positive, and negative accuracy. Only scalar values cross process
  boundaries, enabling logs, reports, and future training graphs.

Focused tests cover raw-input release, same-file reuse, validation references,
structured events, selected-iteration evaluation, and early-stopping behavior.

## Nested multiprocessing pools — not an issue ✓

The originally suspected problem (quadratic process spawning when `build.score()` calls
`evaluation.launch()` inside an Optuna trial) does not occur: Optuna always runs a
single trial at a time, never inside a worker pool, so no nested pools arise.

The observed symptom of ~128 idle threads per evaluation worker was a separate issue:
numpy/scipy/sklearn module-level imports in `builder/svm.py` triggered OpenBLAS+OpenMP
thread pool initialisation in every spawn worker at unpickle time. Fixed by making those
imports lazy.

## RemoteTalker fixes ✓

Removed `log_config`, `log_start`, `log_stop` from `RemoteTalker.REMOTES`.
Having them there caused those calls to be queued to `_local` instead of
executing locally — so `_log_queue` was never set on the proxy and
`log_config` never ran in the child process.

## RemoteTalker queue ownership fixes ✓

- `manager` is now stored as `self._remote_manager` (was a local variable that
  went out of scope immediately, risking premature GC of the Manager server
  process). Explicit shutdown of a default-owned Manager remains tracked in
  `TODO.md`.
- `__init__` accepts an optional `queue` argument: if provided, uses it
  directly (no Manager needed — suitable for fork context); otherwise creates
  a forkserver Manager queue as before (required for spawn workers that need
  to pickle the queue proxy).
- `__getstate__` excludes `_remote_manager` from pickle state.

## Tuning pipeline uses RemoteTalker ✓

The tuning pipeline now wraps the session talker in
`RemoteTalker(talker, queue=multiprocessing.Queue())`. Public talker events are
forwarded to the parent, while queue and logging lifecycle methods execute
locally. Child-side autotuning logging uses talker methods, and the parent
listener drains queued events before returning the tuning result.

## Evaluation interruption propagation ✓

Removed worker-side `SIGINT` suppression. `KeyboardInterrupt` now propagates
out of evaluation workers and the launcher terminates and joins its pool.
Solver subprocesses can briefly outlive terminated workers, but configured
resource limits bound their lifetime.

## Shared training Manager lifecycle ✓

Training collectors now defer shared state creation until a learning session
starts. One forkserver Manager is shared by train and development collectors,
and loop shutdown copies statistics back, disconnects proxies, and explicitly
shuts down the Manager.

## Tuner process-group cleanup ✓

The forked tuner becomes a process-group leader. Interruption terminates the
whole group, waits for the tuner, escalates to `SIGKILL` if needed, and joins
the tuner. This covers nested evaluation pools, data-loading pools, and solver
subprocesses.

## Fork tuner before listener threads ✓

Autotuning now prepares communication queues, forks the tuner, and starts
listener threads only afterwards. Messages produced during startup remain
buffered, avoiding a post-thread fork while retaining the required fork-based
tuner process.

## Talker counters reset per evaluation ✓

`LogTalker.eval_begin()` resets evaluation totals and errors, while
`eval_next()` resets solved, unsolved, and failed task counters for each job.
Reusing one session talker across loop iterations no longer carries these
counters forward.

## Audited process-local solver state ✓

`Solver._output` and `SolverPy._exitcode` are intentionally worker-local.
Evaluation workers return processed results, and no parent behavior relies on
those mutable solver attributes. Normal evaluation also intentionally leaves
worker log forwarding disabled unless a caller explicitly starts it.

## TuneTalker — unified tuning progress talker ✓

Replaced `RemoteTalker(SolverTalker()) + AutotuneListener` with a single
self-contained `TuneTalker(SolverTalker)` in `builder/autotune/tunetalker.py`.

- `TuneTalker` has its own plain `multiprocessing.Queue` (fork-compatible,
  no Manager needed) and a background listening thread.  `__getattribute__`
  intercepts `REMOTES` calls in the forked child and queues them; the parent
  thread dispatches to the real handlers.  `wait()` blocks until the child
  sends `result(val)`.
- All tuning event log-based defaults (`trials`, `trying`, `tried`,
  `trialed`, `building`, `iteration`, `built`, `result`, `tuning`, `tuned`,
  `info`, `debug`) added to `LogTalker`, so headless behavior is inherited
  automatically.  `TuneTalker` overrides only `building`/`iteration`/`built`
  to show a `BuilderBar` in interactive mode.
- `SolverTalker.end()` made defensive (`if self._total_bar:` instead of
  `assert`) so it works correctly when no bar exists (headless mode).
- `prettytuner()` simplified: creates `TuneTalker`, sets `builder.talker`,
  calls `talker.wait()` — the `while True: queue.get()` loop is gone.
- `autotuner.build()` simplified: no more `RemoteTalker`/`LogTalker` import
  or `listening_start()`/`listening_stop()` calls.
- `queue` → `talker` rename throughout `autotune.py`, `build.py`, `check.py`,
  `tune.py`; `queue.put((key, content))` replaced with `talker.key(*content)`
  direct calls.
- `listener.py` (`AutotuneListener`, `Listener`) deleted.

## `solverpy report` — offline HTML from .md report ✓

New CLI subcommand `solverpy report FILE.md [-o FILE.html]` converts a solverpy
report Markdown file (written next to the `.log` by `reporter.py`) into a
self-contained offline HTML page.

- `scripts/report.py`: `convert()` runs Python-Markdown with the same extensions
  as `mkdocs.yml` (`pymdownx.highlight`, `pymdownx.inlinehilite`,
  `pymdownx.superfences`, `tables`); `noclasses=True` so syntax highlighting is
  fully inline (no external CSS dependency); wraps output in a minimal HTML shell
  with embedded CSS (tables, code blocks, headings, max-width layout).
- `scripts/cli.py`: imports and registers `report` subcommand.

## Progress bar improvements ✓

Multiple alignment and style improvements to `SolvingBar`/`RunningBar` displayed
during benchmark evaluation.

**Label alignment** (`benchmark/summary.py`, `task/logtalker.py`, `task/solvertalker.py`):
- Nick width now includes `"total"` in the max calculation, plus `+1` so every
  nick always has at least one trailing space before the tqdm `:` separator.
- `[n/m]` prefix pads the job index to the digit width of the total job count.
- `"total"` bar desc is prefixed with the same number of spaces as `[n/m] ` so
  all descs are the same width and the `|bar|` column starts at the same position.
- Removed `.strip()` on nick in `logtalker.next()` that was discarding padding.
- Nick format changed from `* s1` to `s1*` (star suffix instead of prefix).

**Fixed inner bar width** (`task/bar.py`):
- Replaced tqdm's dynamic `{bar}` with a custom `{bar_fixed}` field injected via
  `format_dict`.  `_build_bar(n, total, colour)` renders exactly `BAR_WIDTH = 46`
  characters using `BAR_CHARS`, with optional ANSI colour wrapping.  tqdm no
  longer resizes the bar based on terminal width or postfix length.

**Postfix alignment** (`task/bar.py`, `task/solvertalker.py`):
- `_postfix_width(total)` computes the maximum visible width of
  `+s/u/!e/?eta` for a given problem count (`6 + 4 * digit_width`).
- `SolvingBar.format_dict` injects `{pad}` spaces to reach that width.
- `RunningBar` accepts a `postfix_width` parameter; `solvertalker` passes
  `_postfix_width(max_job)` so the total bar's `!errors` is padded to the same
  width, aligning the `[elapsed<remaining]` timestamp across all bars.

**Bar characters**: changed from `┈─═━` to `░▒▓█` (block shading style).

## Production setup-key rename ✓

Renamed the two core Setup keys throughout production code and maintained
documentation. The legacy root README and benchmark tests still need updating
and are tracked in `TODO.md`.

- `setups/setup.py`: TypedDict fields and docstring updated
- `benchmark/evaluation.py`: `launch()` signature updated
- `setups/loop.py`: all `setup["sidlist"]` / `setup["bidlist"]` references updated
- `data/setups/eval-eprover.yml`: uses new key names
- `docs/tutorial.md`, `docs/index.md`: code examples and table updated
- `docs/dia/solverpy-benchmark.puml`, `docs/dia/solverpy-ml.puml`: field names updated
- `docs/dia/solverpy-benchmark.svg`, `docs/dia/solverpy-ml.svg`: inline text updated

## Plugin repr audit and fixes ✓

Audited all plugins in `solverpy` and `solverpy-learn` for constructor args reaching
`SolverPyObj.__repr__`. Fixed gaps so `repr()` and `represent()` are consistent.

- `solver/plugins/plugin.py`: forward `pid` to `SolverPyObj.__init__` when set, so
  named plugins (e.g. `Outputs(pid="outputs")`) show their id in repr
- `solver/plugins/apply.py`: forward `fn.__name__` so `Apply(fn=foo)` shows in repr
- `builder/plugins/trains.py`: add `**kwargs` to `Trains.__init__` and forward to
  `Decorator.__init__`, allowing subclasses to pass extra params through to repr
- `builder/plugins/svm.py`: add `**kwargs`, pass `chunk_size` to `Trains.__init__`
- `builder/plugins/enigma.py`: pass `features`, `variant`, `ratio` to `SvmTrains.__init__`;
  add `EnigmaTrainsDebug.represent()` returning `cls`, `variant`, `ratio`
- `builder/plugins/cvc5.py`: pass `ratio` to `SvmTrains.__init__`;
  add `Cvc5Trains.represent()` extending parent with `ratio`;
  add `Cvc5TrainsDebug.represent()` returning `cls`, `ratio`
- `builder/plugins/multi.py`: add `MultiTrains.represent()` returning `cls`, `dataname`,
  `trains` (list of sub-train reprs); `EnigmaMultiTrains` inherits this

## Bundled setup YAML files, copied by `solverpy init` ✓

Added `data/setups/` alongside `data/strats/` for bundled example YAML setup files.
`solverpy init <solver>` now copies `data/setups/eval-<solver>.yml` to cwd if it exists.

- `data/setups/eval-eprover.yml`: example YAML for eprover evaluation
- `scripts/init.py`: after copying strats, checks for `data/setups/eval-{solver}.yml`
  and copies it to cwd; covered by the existing `data/**/*` package-data glob

## `solverpy run file.yml`, `solverpy clean`, options docs ✓

Added two more CLI subcommands and fixed the log filename.

- `scripts/run.py`: new `solverpy run FILE` subcommand; loads YAML, pops `evaluate`
  key to select solver via `setups.<solver>()`, then calls `setups.evaluation()` and
  `setups.launch()`; calls `log.init(filename)` early so the log is named after the
  YAML file (e.g. `eval-eprover.yml.log`) rather than the script path
- `scripts/clean.py`: new `solverpy clean` subcommand; requires `solverpy_db/` in cwd,
  deletes all its subdirectories except `strats/`, prompts for confirmation unless `-y`
- `tools/log.py`: `init()` and `filename()` accept optional `name` parameter; `init()`
  is now idempotent (returns early if already initialised); falls back to
  `os.path.basename(sys.argv[0])` when no name given
- `dust/eval-eprover.yml`: example YAML setup file for the `solverpy run` command
- `setups/setup.py`, `docs/options.md`: added missing options `proofs`, `premises`,
  `headless` to the options table

## `solverpy init [solver]` CLI command ✓

Bundles strategy files into the package and adds a `solverpy init` subcommand that
populates `solverpy_db/strats/` in the current directory from the bundled data.

- `packages/solverpy/src/solverpy/data/strats/` — strategy files moved here from repo
  root `strats/`; declared as package data via `[tool.setuptools.package-data]`
  `solverpy = ["data/**/*"]` in `pyproject.toml`
- `scripts/init.py` — new module; `register()` wires the argparse subcommand; `main()`
  copies bundled strats to `solverpy_db/strats/`; with no solver arg all files are
  copied with original names; with solver arg only that solver's files are copied,
  stripping the `solver-` prefix
- `scripts/cli.py` — replaces the `init` stub with a real `init.register()` call

## Legend numbered, summary/statuses/bars use legend references ✓

Legend entries now use `s{n}` (1-indexed) instead of strategy names, so bid is never
dropped from the summary.  All three output surfaces updated consistently:

- `benchmark/summary.py`: `legend()` now generates `s1`, `s2`, … nicks (`* s{n}` for
  ref); legend table always shows all five columns `#`, `strategy`, `benchmark`,
  `solver`, `problems` regardless of `sidnames` flag.
- `task/logtalker.py`: `begin()` stores `_total_jobs` and initialises `_job_index = 0`;
  `next()` increments the index and formats `_job_desc` as `[{i}/{n}] s{k}`, so each
  per-job progress bar label references the legend number.

## `represent()` for Builder and Trains hierarchies ✓

Added structured YAML representations for ML builder and training-data plugin classes,
so the setup dump shows readable dicts instead of flat repr strings.

- `Builder.represent()` → `{cls, dataname}`
- `AutoTuner.represent()` → `{cls, dataname, tuneargs, templates}`
- `Trains.represent()` → `{cls, dataname, filename}`
- `SvmTrains.represent()` → adds `chunk_size`
- `EnigmaTrains.represent()` → adds `features`, `variant`, `ratio`

## Combined setup+devels YAML dump ✓

`evaluation.init()` now accepts a `devels` argument and dumps both as a single YAML
block `{setup: ..., devels: ...}` using PyYAML's default anchor/alias for shared objects
(e.g. the same `EnigmaTrains` instance appearing in both `trains` and `plugins`).

- `benchmark/evaluation.py`: `init(setup, devels=None)` passes devels to `markdown.yaml`
- `benchmark/reports/markdown.py`: `yaml(obj, devels=None)` wraps both under `setup:`/`devels:`
- `solverpy_learn/setups/loop.py`: `launch()` passes `devels` to `evaluator.init()`

## Fix forkserver-in-fork-child crashes ✓

Two crash sites where `forkserver` pools were started from inside `prettytuner`'s fork
child, causing `ChildProcessError: No child processes` (forkserver's `os.waitpid` only
works for direct children of the calling process, not inherited grandchildren).

- `builder/svm.py`: three `forkserver` Pools → `fork` (rawcompress, load×2 — always
  called from inside the prettytuner fork child; `fork` is cheaper and correct here)
- `task/launcher.py`: add `pool_context: str = "forkserver"` parameter to `launch()`
- `builder/autotune/build.py`: atpeval setup sets `pool_context="spawn"` so the
  evaluation pool launched from inside the fork child uses spawn (safe, clean workers)
- `setups/setup.py`: add `pool_context` key to `Setup` TypedDict

## Switch all multiprocessing contexts to `forkserver` ✓

Unified all `multiprocessing` start methods to `"forkserver"` across the codebase,
replacing the previous mix of `"fork"` (autotune, Managers, SVM pools) and `"spawn"`
(evaluation pool, log/remote talker Managers).  `forkserver` gives clean workers like
`spawn` (no unsafe post-thread fork) but fast startup like `fork`, and is now the
Python 3.14 Linux default.

Files changed:
- `task/launcher.py` — two `"spawn"` Pools → `"forkserver"`
- `task/talker.py` — `"spawn"` Manager → `"forkserver"`
- `task/remotetalker.py` — `"spawn"` Manager → `"forkserver"`
- `builder/autotune/autotune.py` — `"fork"` Process+Queue → `"forkserver"` *(later reverted, see below)*
- `builder/plugins/trains.py` — `"fork"` Manager Lock → `"forkserver"`
- `builder/plugins/svm.py` — `"fork"` Manager Namespace → `"forkserver"`
- `builder/svm.py` — three `"fork"` Pools → `"forkserver"`
- `tools/external.py` — `"fork"` → `"forkserver"` (dead code, kept as infrastructure)
- `grackle/runner/runner.py` — bare `Pool` → `get_context("forkserver").Pool`

## Reporter (.md sidecar) ✓

Added a module-level `reporter` (mirroring how the `logging` module works) that writes
a `.md` file next to the `.log` file, capturing experiment progress as clean markdown
without the `"> "` log prefix.

- `tools/reporter.py`: new singleton; `init(logpath)` opens the `.md` file; `add(report)`
  calls `markdown.dump` and writes it; `close()` flushes on exit; `fence(lang)` decorator
  stubs a super-fence registry for future handlers (e.g. render graph data → SVG).
- `tools/log.py`: `init()` calls `reporter.init()` after opening the log file;
  `terminating()` calls `reporter.close()`; `logfile()` accessor added.
- Tables written to `.md`: evaluation setup (`benchmark/evaluation.py`), legend and
  summary (`benchmark/summary.py`), per-job progress (`benchmark/reports/progress.py`),
  autotune trial results (`builder/autotune/listener.py`).

## `prettytuner` switched back to `"fork"` ✓

`prettytuner` was moved to `"forkserver"` during the multiprocessing unification, but
investigation showed this was the wrong choice: the builder carries accumulated
`_trains` and `_devels` data that must be pickled on every call under `forkserver`,
growing with each loop iteration.  With `"fork"` the child inherits the parent's memory
and none of this is serialised.

The `"forkserver"` migration also caused a one-time ~3 s daemon startup delay and
required `RemoteTalker` pickling fixes (see below).  `"fork"` is safe here since
`prettytuner` is called from the main thread before any worker pools are started.

- `builder/autotune/autotune.py`: `get_context("forkserver")` → `get_context("fork")`

## `RemoteTalker` pickling fix ✓

Under Python 3.14 forkserver, `RemoteTalker` failed to pickle because its
`_listening_thread` (a `threading.Thread`) and `_stop_listening` (a
`threading.Event` wrapping a `_contextvars.Context`) are not serialisable.

Fixed with `__getstate__`/`__setstate__`: the thread and event are set to `None` in
the pickled state and a fresh `Event` is reconstructed on unpickle.  The child only
needs `_remote_queue` to put events; the listening thread lives in the parent only.

- `task/remotetalker.py`: added `__getstate__` and `__setstate__`.

## `Talker.log_config` log level fix ✓

`log_config()` was setting the root logger to `INFO` in child processes, silently
dropping all `DEBUG` messages even when the parent's handlers were configured at
`DEBUG`.  Fixed to `DEBUG`.

- `task/talker.py`: `root.setLevel(logging.INFO)` → `root.setLevel(logging.DEBUG)`

## Posneg Weight Tuning Phase ✓

Added phase `"w"` (weight) to the autotuner that tunes `scale_pos_weight` by
trying multipliers `[0.5, 1, 2, 3, 5, 10]` against the balanced base ratio
(`neg/pos`).  Enabled by including `"w"` in the `phases` string, e.g.
`phases="l:b:m:r:w"`.

- `autotune.py`: registers `"w": tune.posneg_weight`; sets `scale_pos_weight =
  neg/pos` as the base when `"w"` is active instead of `is_unbalance`.
- `tune.py`: `posneg_weight()` freezes the base at phase-start time as
  `posneg_base` to prevent double-multiplication if `"w"` appears twice.
- `check.py`: `posneg_weight()` suggests the final `scale_pos_weight` value
  (base × multiplier); logs the human-readable multiplier in the queue.

## Lazy imports in `builder/svm.py` ✓

`builder/svm.py` previously imported `numpy`, `scipy`, and `sklearn` at module
level.  Because `SvmTrains`/`EnigmaTrains` plugins are pickled into every
`SolverTask` and sent to spawn pool workers, unpickling in each worker triggered
the full import chain — initialising an OpenBLAS thread pool (via numpy/scipy)
and an OpenMP thread pool (via sklearn) in every worker process.  With
`OMP_NUM_THREADS=64` and `cores=64` this created 64 × ~128 = ~8 000 idle threads
during evaluation, when none of those libraries are used.

Fixed by moving all three imports inside the functions that actually call them
(`_chunk_save`, `_chunk_compress`, `_chunk_load`, `_chunk_stack`, `_raw_compress`,
`_raw_load`, `load`, `decompress`).  Importing the module no longer loads any
heavy library.

## Bug Fixes ✓

- **Debug code in `launcher.launch()`** (`task/launcher.py:57–71`) — wrote to `~/debug.log`
  and iterated all solver attributes with `dir()` on every call; removed.
- **Mutable default argument in `SolverTask.__init__`** (`task/solvertask.py:28`) —
  `calls: list[...] = []` was shared across instances; fixed with `None` default.
- **File resource leak in `Outputs.write()`** (`solver/plugins/db/outputs.py:72–76`) —
  `fw.close()` not in `with` block; fixed.
- **Manager queue lifecycle** (`task/talker.py:87`) — `Manager().Queue()` created a
  Manager subprocess never cleaned up on crash; fixed.

## Re-using Trains ✓

Previously collected training data (`train.in`) is reused across loop iterations
instead of being regenerated from scratch each time.

## svm.py Helper Refactoring ✓

Renamed and regrouped private helpers in `builder/svm.py` with `chunk_`/`raw_`
group prefixes:

- `chunkpath` → `chunk_path`, `chunkfiles` → `chunk_files`, `ischunked` → `chunk_exists`
- `_save_chunk` → `_chunk_save`, `_compress_batch` → `_chunk_compress`
- `_load_chunk` → `_chunk_load`, `_stack_pairs` → `_chunk_stack`
- `rawchunkpath` → `raw_path`, `rawchunkfiles` → `raw_files`, `israwchunked` → `raw_exists`
- `_compress_raw` → `_raw_compress`, `_load_rawchunk` → `_raw_load`

Functions reordered so chunk_/raw_ groups are contiguous.  `svm.compress` now
dispatches rawchunk compression internally (moved from `SvmTrains.compress`),
making the plugin layer a simple passthrough.  Fixed 3 pyright type errors by
typing chunk/raw loaders as returning `csr_matrix` and using per-element shape
assertions in `_chunk_stack`.

## Chunking in SvmTrains (Raw Files) ✓

Write training data directly as fixed-size raw text chunks during `save()` instead
of appending to a single `train.in` file.  Eliminates the separate compress pass
and enables parallel NPZ compression.  Fixes `merge()` for the `no-compress` case
since raw text chunks are merged by relinking.

- `SvmTrains.__init__`: `info.line_count`, `info.raw_chunk_n`, `info.chunk_size`
  in the Manager Namespace so all spawn workers share values.
- `SvmTrains.save()`: rolls over to a new raw chunk when `chunk_size` is exceeded.
- `raw_path`, `raw_files`, `raw_exists`, `_raw_compress`, `_raw_load` in `svm.py`.
- `rawcompress()` compresses raw chunks in parallel via `Pool.starmap`.
- `merge()`, `format()`, `exists()`, `size()` handle the `text/raw-chunks` format.

## Parallel Loading of Chunks ✓

`load()` in `builder/svm.py` now loads NPZ chunks and raw text chunks in
parallel via a fork-context `Pool`.  Single-chunk case skips the pool.
`_chunk_stack()` helper deduplicates the vstack/normalize logic shared by
both formats.

## Chunked Training Data ✓

Split large SVM-Light training files into fixed-size NPZ chunks to handle
100 GB+ datasets without loading everything into RAM at once.

Current flow: `train.in` (text) → `compress()` → single `train.in-data.npz` +
`train.in-label.npz`.  At 100 GB / ~200M rows this requires holding the full
sparse matrix in RAM during compression and merge.

Chunked flow: same `train.in` text → N chunk files, each covering `chunk_size`
rows.  Loading globs all chunks and vstacks.  Merge appends chunk lists.

File layout:

```
train.in                          # text, appended during evaluation (unchanged)
train.in-chunk0000-data.npz       # rows 0 .. chunk_size-1
train.in-chunk0000-label.npz
train.in-chunk0001-data.npz       # rows chunk_size .. 2*chunk_size-1
train.in-chunk0001-label.npz
...
```

Chunk size default: **1 000 000 rows** (≈ 512 MB of SVM-Light text at 512 B/row).
User-configurable via `setup["chunk_size"]`.
