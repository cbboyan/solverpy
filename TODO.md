# Chunking in SvmTrains (Raw Files)

Write training data directly as fixed-size raw text chunks during `save()` instead
of appending to a single `train.in` file.  This eliminates the separate compress
pass and enables parallel NPZ compression.  Also fixes `merge()` for the
`no-compress` case, since raw text chunks can be merged by relinking (same O(1)
cost as NPZ chunk merge).

## Changes

### `builder/plugins/svm.py`

- `SvmTrains.__init__`: add `self.info.line_count = 0`, `self.info.raw_chunk_n = 0`,
  `self.info.chunk_size = chunk_size` to the Manager Namespace so all spawn workers
  share the values.

- `SvmTrains.save()` (override `Trains.save()`): count lines in `samples`; if
  adding them would exceed `chunk_size`, increment `raw_chunk_n` and reset
  `line_count`; append to `{path}-raw{raw_chunk_n:04d}`; update `line_count`.
  Policy: finish writing the current call even if it slightly overshoots the limit,
  then roll over for the next call.  All under the existing Manager lock.

- `SvmTrains.compress()`: gather all `train.in-raw*` files and compress in
  parallel via `Pool.starmap(svm.compress_raw, [...])`.

### `builder/svm.py`

- `rawchunkpath(f_in, n)` — `f"{f_in}-raw{n:04d}"`.

- `rawchunkfiles(f_in)` — glob for `{f_in}-raw*`.

- `compress_raw(raw_path, f_in, n)` — read raw text file, call
  `load_svmlight_file`, call `save_chunk`.  This is the function mapped across
  the parallel compression pool.

- `merge()` — extend to handle raw text chunks: link/rename with sequential
  numbering (no loading needed).

- `format()` / `exists()` / `size()` — add `"text/raw-chunks"` case.

### `setups/loop.py`

- `trains_compress()` unchanged — still triggers after evaluation.  Now it
  dispatches parallel compression of raw chunks instead of reading one big file.

## Design notes

- `chunk_size` must be stored in `info.chunk_size` (Manager Namespace) so spawned
  workers see the value set in the main process before evaluation starts.
- `no-compress` path produces raw text chunks; `merge()` handles them by relinking.

---

# Python 3.14 fork/spawn Considerations

Python 3.14 changed the Linux default multiprocessing start method from `"fork"`
to `"forkserver"`.  Initial fixes applied, but the root cause (ISSUES.md #4:
nested pool → quadratic process blowup) that motivated the mixed `"fork"` /
`"spawn"` strategy has not been addressed.  May require revisiting the whole
approach.

Fixed so far:
- `tools/external.py` — `@external` decorator: explicit `"fork"` Process+Queue
- `benchmark/db/provider.py` — `_ProviderMaker` module-level (was local class)
- `builder/autotune/autotune.py` — `prettytuner`: explicit `"fork"` Process+Queue
- `builder/plugins/trains.py` — Manager Lock: `"fork"` context
- `builder/plugins/svm.py` — Manager Namespace: `"fork"` context
- `test_learn_loop.py` fixture — use `os.path.relpath()` for `SOLVERPY_DB` and
  `SOLVERPY_BENCHMARKS` (eprover-ho prepends `ENIGMATIC_ROOT` defaulting to `"."`;
  absolute paths produced `.//absolute/path` which fails)

Deferred: ISSUES.md #4 (nested pool → quadratic process blowup) is the root
cause why `"spawn"` was introduced.  Address that separately.

---

# Parallel Loading of Chunks

Load NPZ chunks (and raw text chunks) in parallel.  Currently `load()` is a
sequential loop; each chunk is independent so a pool can be dropped in with
minimal structural change.

## Changes

### `builder/svm.py`

- `load()` for chunked NPZ: replace the `for` loop with a parallel load (e.g.
  `Pool.starmap` or `joblib.Parallel`) that loads `(data, label)` pairs
  concurrently, then `vstack` + `concatenate` as now.

- `load()` for raw text chunks (new, added alongside chunking-in-SvmTrains):
  parallel `load_svmlight_file` across raw chunk files, then `vstack` +
  `concatenate`.

## Design notes

- Both chunked formats (NPZ and raw text) are already loops over independent
  pairs, so the parallelism is straightforward.
- Decide between `joblib.Parallel` (already a dependency?) and a plain
  `multiprocessing.Pool` when implementing.

---

---

# DONE

## Chunked Training Data ✓

Split large SVM-Light training files into fixed-size NPZ chunks to handle
100 GB+ datasets without loading everything into RAM at once.

## Motivation

Current flow: `train.in` (text) → `compress()` → single `train.in-data.npz` +
`train.in-label.npz`.  At 100 GB / ~200M rows this requires holding the full
sparse matrix in RAM during compression and merge.

Chunked flow: same `train.in` text → N chunk files, each covering `chunk_size`
rows.  Loading globs all chunks and vstacks.  Merge appends chunk lists.

## File layout

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

## Changes

### `builder/svm.py`

- `chunkfiles(f_in) -> list[tuple[str, str]]`
  Glob for `f_in-chunk*-data.npz`, return list of `(data_path, label_path)` pairs
  sorted by name.

- `ischunked(f_in) -> bool`
  `len(chunkfiles(f_in)) > 0`

- `compress(f_in, keep=False, chunk_size=1_000_000)`
  Read `train.in` line-by-line; accumulate `chunk_size` lines; call
  `load_svmlight_file` on each batch (via `io.StringIO`) and `save_chunk()`.
  Delete text file unless `keep=True`.

- `save_chunk(data, label, f_in, n)`
  Save one chunk pair: `f_in-chunk{n:04d}-data.npz` / `-label.npz`.

- `load(f_in) -> (spmatrix, ndarray)`
  1. `ischunked` → load all chunks, `scipy.sparse.vstack` + `numpy.concatenate`
  2. plain text → `load_svmlight_file` (unchanged, during collection)

- `size(f_in)`  
  Sum sizes of all chunk files (or text file).

- `format(f_in)`  
  Return `"binary/chunks"` | `"text/svm"` | `"unknown"`.

- `link(src, dst)`  
  Symlink all chunk file pairs.

- `merge(f_in1, f_in2, f_out)`  
  Append chunks: copy/link all chunks from `f_in1` into `f_out` as
  0000..N-1, then all chunks from `f_in2` as N..N+M-1.  No full load needed.

- `save(data, label, f_in)` — **remove** (replaced by `save_chunk`; only used
  internally by old `compress`).

- `decompress(f_in, keep=True)`  
  Load all chunks, dump combined matrix to text via `dump_svmlight_file`.

### `builder/plugins/svm.py`

- `SvmTrains.compress(self, chunk_size=1_000_000)`  
  Pass `chunk_size` through to `svm.compress()`.

### `setups/loop.py`

- `trains_compress(setup)`  
  Pass `setup.get("chunk_size", 1_000_000)` to `trains.compress()`.

### `setups/setup.py`

- Add `chunk_size: int` key with comment.

## Parameters

| Parameter | Default | Where to set |
|---|---|---|
| `chunk_size` | `1_000_000` | `setup["chunk_size"]` |

## Design notes

1. **`merge()` strategy** — append chunks from addon to train (renumber
   sequentially).  No re-chunking.  Chunk count grows across loops; that is fine.

2. **Backward compat reads** — old single `-data.npz` / `-label.npz` format
   dropped completely.  Rename files manually if migration needed.

3. **`joblib` parallelization** — implement first without it; add in a follow-up.
   Design `compress()` and `load()` as loops over independent chunks so joblib
   can be dropped in with minimal changes later.

4. **`deconflict()`** — keep as full-load operation for now (not in main loop).

5. **Chunk filename zero-padding** — 4 digits sufficient: 9999 chunks × 1M rows
   × 512 B/row ≈ **5 TB** of SVM-Light text.

