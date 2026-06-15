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

   Status: fixed and verified for E. cvc5ml still needs the equivalent
   migration; until it lands, the `setup["solver"]` fallback (see point 10)
   keeps cvc5 working. Verified by the E-vs-cvc5 divergence in
   `test_train_has_model_build_loops` (E train has only `loop00`/`loop01`; the
   unmigrated cvc5 still writes a spurious `loop02` from the final devel-only
   evaluation) and by `test_eprover_configures_independent_evalset_solvers`.

   Each `setups.eprover(..., key=...)` appends another plugin to the shared
   `setup["plugins"]` and rebuilds the same `setup["solver"]`. Both collectors
   use plugin id `"trains"`.

   Consequently, a devel evaluation can write training examples into both
   train and devel collectors, and the train evaluation can do the same. Each
   evaluation must activate only its selected collector. Per-evalset solver
   ownership is the cleaner design and restores the old behavior without
   duplicating the whole `Setup`.

   One `setups.eprover(setup)` call now creates an independent solver and
   collector for every present evalset. E solvers are stored in
   `evalset["solver"]`; E no longer stores a constructed solver in the root
   setup.

3. **Nested `solvedby` is ignored.**

   Status: open (tuning side partially addressed). `build.score()` now strips
   `solvedby` from its evalset copy so tuning is not restricted
   (`test_score_does_not_restrict_tuning_evaluation_with_solvedby`). But normal
   evaluation still reads `solvedby` only from the root setup via `**others`;
   nested `setup["trains"]["solvedby"]` is not forwarded, and `solvedby` is
   still absent from the `Evalset` TypedDict.

   `evaluation.launch()` extracts `benchmarks`, `strategies`, `ref`, and
   `proofs` from the evalset, but accepts `solvedby` only from the outer
   `Setup`. Thus `setup["trains"]["solvedby"]` has no effect.

   Add `solvedby` to `Evalset` and pass it to `evaluation.run()` from the
   selected evalset. A general helper that merges shared setup fields with the
   selected evalset would prevent similar omissions.

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

   Status: fixed for E. cvc5ml still uses the old arguments.

   `eprover()` and `cvc5()` should infer training configuration from the
   selected evalset:

   ```python
   setups.eprover(setup, key="trains")
   setups.eprover(setup, key="devels")
   ```

   Alternatively, configure all present evalsets in one call. Remove
   `training=True`.

7. **Solver static options are keyed incorrectly.**

   Status: fixed for E. cvc5ml still needs the equivalent migration.

   Training-output flags are added only when `key == "trains"`. A devel-only
   training evalset therefore lacks the required E/cvc5 output flags. Make
   static-option insertion idempotent and independent of which evalset is
   configured.

8. **Normalization defeats `"trains" in setup`.**

   Status: open, and now load-bearing. `experiment()` still synthesizes a
   `trains` evalset unconditionally, and the refactor now *depends* on that:
   base `eprover()` asserts `"trains" in setup`, and `evalsets()`/`iteration()`
   assume trains is present. Dropping the synthesized evalset now requires
   making those call sites tolerate an absent `trains` first.

   `experiment()` always creates an empty `trains` evalset, even for an empty
   setup. Therefore presence cannot indicate that training was requested.

   Since backward compatibility is not required, simplify normalization around
   the canonical nested form and do not synthesize absent evalsets.

9. **One obsolete `(setup, devels)` API remains.**

   Status: mostly resolved. The only caller now passes a single setup
   (`markdown.yaml(setup)` in `evaluation.py`); the vestigial `devels=None`
   parameter on `markdown.yaml()` is unused and should be removed.

   `benchmark.reports.markdown.yaml()` still accepts a separate `devels`
   argument. It should accept only the self-contained setup.

10. **Autotune scoring must use the same solver fallback.**

    Status: fixed (this audit).

    `builder/autotune/build.py::score()` originally looked up the evaluation
    solver as `setup["solver"]`. The Evalset refactor changed it to
    `devels["solver"]`, which crashed cvc5 tuning (`cvc5-atpeval`): cvc5 is
    unmigrated and only sets the root `setup["solver"]`, never
    `devels["solver"]`. The tuner child died and `prettytuner` returned `None`
    (`TypeError: cannot unpack non-iterable NoneType`).

    Resolved by mirroring `evaluation.launch`'s own fallback:

    ```python
    solver = devels.get("solver", setup.get("solver"))
    assert solver is not None
    ```

    **Solver-resolution contract.** Prefer the per-evalset `evalset["solver"]`
    (set by migrated E, which pops the root `setup["solver"]`); fall back to the
    shared root `setup["solver"]` (set by unmigrated cvc5/vampire/z3). Both
    `evaluation.launch` and `build.score` depend on this. The root fallback can
    only be removed once every solver setup attaches per-evalset solvers
    (points 2/6/7 for cvc5).

## Intended Loop Shape

```python
prepare_evalset(setup, "devels")
if not final_validation_iteration:
   prepare_evalset(setup, "trains")
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
  `devel eval -> devel extract -> train eval -> train extract -> one build`
  (`test_launch_prepares_both_evalsets_then_builds_once`).
- `[x]` Both evalsets using `start_dataname`
  (`test_iteration_applies_both_start_datanames_before_build`).
- `[ ]` Only one evalset using `start_dataname`.
- `[~]` Normal evaluation forwards nested `solvedby`; tuning removes it. Only
  the tuning-removes half is tested
  (`test_score_does_not_restrict_tuning_evaluation_with_solvedby`); nested
  forwarding is still unimplemented (point 3).
- `[x]` Devel evaluation writes only devel data and train evaluation only train
  data (`test_eprover_configures_independent_evalset_solvers`, plus the
  behavioral E-vs-cvc5 divergence in `test_train_has_model_build_loops`).
- `[ ]` Initial builder path is `trains/.../loop00` (loop00 dirs are checked,
  but the builder path itself is not asserted directly).
- `[x]` One build per non-final iteration
  (`test_launch_prepares_both_evalsets_then_builds_once`).
- `[x]` Final iteration remains validation-only (`test_train_has_model_build_loops`
  + `test_devel_has_three_loops`).
- `[ ]` Devel-only setup receives training-output solver flags (point 7).

Remaining gaps cluster on the still-open points (3, 7, 8) and the cvc5
migration.
