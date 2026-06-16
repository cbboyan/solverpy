# Setup/Evalset Refactor Regressions

The refactor after commit `4989b847c65dc11abca828be74c548f201a4b2ac`
made `Setup` self-contained by nesting the training and development evaluation
sets under `setup["trains"]` and `setup["devels"]`. The current implementation
does not preserve all previous learning-loop behavior.

## Findings

1. **Model building runs twice and too early.**

   Status: fixed and verified (learn loop suite + `test_runtime`).

   `solverpy_learn.setups.loop.oneloop()` builds after each evalset. Since
   `devels` runs first, the first build sees unprepared training data; `trains`
   then triggers another build.

   `model_build()` must move into `launch()` and run once after:

   1. prepare/evaluate `devels`
   2. prepare/evaluate `trains`
   3. build one model

   `oneloop()` now only prepares one evalset. Iteration orchestration prepares
   development data, prepares training data, and calls `model_build()` once.
   The final iteration remains development-only when `devels` is configured.

2. **Both data collectors are attached to one solver.**

   Status: fixed and verified for E and cvc5ml. cvc5 now configures
   independent per-evalset solvers, and the root `setup["solver"]` fallback has
   been removed.

   Each `setups.eprover(..., key=...)` appends another plugin to the shared
   `setup["plugins"]` and rebuilds the same `setup["solver"]`. Both collectors
   use plugin id `"trains"`.

   Consequently, a devel evaluation can write training examples into both
   train and devel collectors, and the train evaluation can do the same. Each
   evaluation must activate only its selected collector. Per-evalset solver
   ownership is the cleaner design and restores the old behavior without
   duplicating the whole `Setup`.

   One solver setup call now creates an independent solver and collector for
   every present evalset. Solvers are stored in `evalset["solver"]`; constructed
   solvers are no longer stored in the root setup.

3. **Nested `solvedby` is ignored.**

   Status: fixed. `solvedby` is part of `Evalset`, `evaluation.launch()` lets
   selected evalset execution keys override root setup keys, and `build.score()`
   still strips `solvedby` from its evalset copy so tuning is not restricted
   (`test_score_does_not_restrict_tuning_evaluation_with_solvedby`).

4. **The initial builder path is not reset to `loop00`.**

   Status: fixed.

   Initial `loopinit()` changes the training dataname to `.../loop00`, but
   `builder.reset()` is called only for later iterations. Before the refactor,
   initial `loopinit()` reset the builder too.

   Reset the builder immediately after initializing `trains` for every
   iteration, including iteration zero.

5. **`start_dataname` only works accidentally until the premature build.**

   Status: fixed by the point 1 sequencing change.

   The per-evalset skip/reset logic is reasonable, but the devel-triggered
   build reads both plugins before the training-side `start_dataname` has been
   applied. Moving the build after both preparation steps fixes this.

   Required iteration-zero order:

   ```text
   prepare devels, applying devels.start_dataname
   prepare trains, applying trains.start_dataname
   builder.reset(trains.dataname)
   build using trains.plugin.path() and devels.plugin.path()
   ```

6. **`training=True` is now redundant and obscures the intended API.**

   Status: fixed for E and cvc5ml.

   Solver setup configures all present evalsets in one call. cvc5 no longer
   accepts `training=True`.

7. **Solver static options are keyed incorrectly.**

   Status: fixed for E and cvc5ml.

   Training-output flags are added only when `key == "trains"`. A devel-only
   training evalset therefore lacks the required E/cvc5 output flags. Make
   static-option insertion idempotent and independent of which evalset is
   configured.

8. **Normalization defeats `"trains" in setup`.**

   Status: fixed. `experiment()` now normalizes the canonical nested form,
   accepts `trains` only as an input alias for `evals`, merges `common` into
   present evalsets, and no longer synthesizes absent evalsets.

9. **One obsolete `(setup, devels)` API remains.**

   Status: fixed.

   `benchmark.reports.markdown.yaml()` accepts only the self-contained setup.

10. **Autotune scoring must use the same solver fallback.**

   Status: superseded by the full per-evalset solver migration.

    `builder/autotune/build.py::score()` originally looked up the evaluation
    solver as `setup["solver"]`. The Evalset refactor changed it to
    `devels["solver"]`, which crashed cvc5 tuning (`cvc5-atpeval`): cvc5 is
    unmigrated and only sets the root `setup["solver"]`, never
    `devels["solver"]`. The tuner child died and `prettytuner` returned `None`
    (`TypeError: cannot unpack non-iterable NoneType`).

    Resolved by mirroring `evaluation.launch`'s own fallback:

    ```python
    solver = devels["solver"]
    ```

    **Solver-resolution contract.** Every solver setup attaches solvers to
    `evalset["solver"]`. `evaluation.launch` and `build.score` require the
    selected evalset to own its solver.

11. **Empty generated train data crashes the learning loop report.**

    Status: fixed and verified with `loop-eprover-atpeval.yml`.

    When `max_proofs` filters out every new proof, `addon.in` is absent but the
    loop still tries to report stats for it. The reporting step now treats a
    missing generated file as an empty generated set and continues with the
    current merged trains.

## Intended Loop Shape

```python
prepare_evalset(setup, "devels")
if not final_validation_iteration:
   prepare_evalset(setup, "evals")
   build_model(setup)
```

`prepare_evalset()` should handle evaluation or `start_dataname`, compression,
merging, statistics, the selected collector/solver, and evalset-specific
options such as `solvedby`.

The final validation-only iteration can retain the previous behavior:
evaluate `devels`, then stop without generating another model.

## Tests Needed

Status key: `[x]` covered, `[~]` partially covered, `[ ]` still missing.

- `[x]` Exact event order
  `devel eval -> devel extract -> eval eval -> eval extract -> one build`
  (`test_launch_prepares_both_evalsets_then_builds_once`).
- `[x]` Both evalsets using `start_dataname`
  (`test_iteration_applies_both_start_datanames_before_build`).
- `[ ]` Only one evalset using `start_dataname`.
- `[x]` Normal evaluation forwards nested `solvedby`; tuning removes it
  (`test_score_does_not_restrict_tuning_evaluation_with_solvedby` covers the
  tuning side; evalset override behavior is covered by normalization and launch
  tests).
- `[x]` Devel evaluation writes only devel data and primary evaluation writes
  only primary data (`test_eprover_configures_independent_evalset_solvers`,
  `test_cvc5_configures_independent_evalset_solvers`).
- `[ ]` Initial builder path is `trains/.../loop00` (loop00 dirs are checked,
  but the builder path itself is not asserted directly).
- `[x]` One build per non-final iteration
  (`test_launch_prepares_both_evalsets_then_builds_once`).
- `[x]` Final iteration remains validation-only (`test_train_has_model_build_loops`
  + `test_devel_has_three_loops`).
- `[x]` Devel-only setup receives training-output solver flags (point 7).
- `[x]` No-new-proofs reuse path keeps reporting alive
  (`test_oneloop_allows_empty_generated_data`).

Remaining gaps are the narrowly scoped tests still marked `[ ]`.
