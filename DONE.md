# DONE

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
