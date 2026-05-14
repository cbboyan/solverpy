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

# Backlog

- automated restriction to solvable problems (force implementation)
- trains regeneration
- show best iteration in the training report
- show the initial model in the report
- reporting
- progress web api
- improve total bar ETA by not including skipped problems
- improve ETA by considering timeout
- nice ntfy messages
- solverpy command script
  - `solverpy init`
  - `solverpy init eprover`
  - `solverpy eval sid bid`
  - `solverpy tune train.in`
  - `solverpy loop bid-train bid-devel`
  - `solverpy launch setup.yaml`
  - launch stuff using command script instead of python scripts
- yaml formatter: use global variables (like `trains`) instead of references `&`
- scripts update
- simulated runs from previous outputs
