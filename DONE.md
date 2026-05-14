# DONE

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
