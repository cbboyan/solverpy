# TASK2: Split Setup Config From Runtime State

## Goal

Replace the current mutable `Setup` typed-dict-as-everything pattern with an
explicit experiment object that separates user configuration from live runtime
state.

This is intentionally a later, larger refactor. `TASK1.md` should first make
`experiment()` the session entry point and clean up the launch/runtime lifecycle.
After that is stable, this task can simplify the data model.

Backward compatibility is not a requirement for this refactor. Prefer one clean
API over maintaining both dict-style and object-style flows.

## Current Problem

`Setup` is currently a `TypedDict(total=False)` that is used for several
different roles at once:

- user-provided YAML/Python configuration
- normalized experiment settings
- solver/evalset configuration
- internal live objects such as `db`, `talker`, `builder`, runtime manager state,
  `it`, and `news`
- broad `**setup` forwarding into functions that only need a few values

This makes call boundaries unclear. Deep functions can receive unrelated state,
and code frequently uses dictionary access such as:

```python
setup["options"]
setup["evals"]["solver"]
setup["talker"]
```

The `**setup` pattern was convenient, but it now hides dependencies and mixes
configuration with runtime state.

## Proposed Model

Introduce a real experiment object:

```python
experiment = setups.experiment(user_config)
```

Conceptually:

```python
@dataclass
class Experiment:
   setup: SetupConfig
   runtime: Runtime
```

### `SetupConfig`

Normalized user/configuration data. This should be reasonably serializable and
close to what comes from YAML or a Python dict.

Examples:

- `options`
- `limit`
- `cores`
- `delfix`
- `ntfy`
- `loops`
- `templates`
- `sel_features`
- `gen_features`
- `posneg_ratio`
- `evals`
- `devels`

### `Runtime`

Live internal state and non-configuration objects.

Examples:

- `db`
- `talker`
- manager/log queue
- connected managed plugins
- `builder`
- loop iteration `it`
- generated strategy list `news`

### `Evalset`

Consider making `Evalset` a real class/dataclass too. It has the same problem as
`Setup`: it mixes user data (`benchmarks`, `strategies`, `limit`, `dataname`)
with live/internal objects (`solver`, training `plugin`, plugin list, proofs).

If splitting `Evalset` at the same time is too large, do it after `Experiment`
and `Runtime` are separated.

## API Direction

Target public flow:

```python
from solverpy import setups

exp = setups.experiment(user_config)
setups.eprover(exp)
setups.launch(exp)
```

ML flow:

```python
from solverpy_learn import setups

exp = setups.experiment(user_config)
setups.eprover(exp)
setups.enigma(exp)
setups.launch(exp)
```

Potential later convenience:

```python
exp = setups.experiment(user_config)
setups.enigma(exp)
setups.launch(exp)
```

where `enigma()` configures E Prover when the solver has not already been
configured.

## Call Boundary Rule

Do not introduce new broad `**setup` forwarding.

New orchestration should pass explicit objects or explicit arguments:

```python
evaluation.launch(evalset, runtime)
```

or:

```python
evaluation.launch(evalset, db=runtime.db, talker=runtime.talker)
```

Avoid passing a whole experiment/config object into deep utilities unless the
function genuinely operates on the whole experiment.

## Naming Direction

Follow the repository naming rule from `AGENTS.md` and `CLAUDE.md`:

- prefer single expressive words
- avoid underscores merely to connect phrase words
- use underscores mainly for grouped-prefix families

Good candidate names:

- `Experiment`
- `SetupConfig`
- `Runtime`
- `Evalset`
- `runtime_connect`
- `plugins_connect`
- `model_build`

Avoid verb-first phrase pairs such as `build_model` / `prepare_model`.

## Migration Plan

1. Finish `TASK1.md` first: `experiment()` as entry point, runtime creation
   separated from plugin connection, and evaluation setup folded into
   experiment bootstrap.
2. Add `Experiment` and `SetupConfig` classes.
3. Make `setups.experiment()` construct an `Experiment` from dict/YAML input.
4. Move live objects out of setup/config and into `runtime`.
5. Update solver setup functions to accept `Experiment`.
6. Update builder setup functions to accept `Experiment`.
7. Update launch paths to accept `Experiment`.
8. Replace internal `setup["key"]` access with object attributes.
9. Remove broad `**setup` forwarding from new/updated call paths.
10. Consider converting `Evalset` into a class/dataclass and splitting its live
    state from user config.
11. Remove the old `TypedDict` setup API rather than maintaining both versions.

## Tests

Add focused tests for:

- `setups.experiment(dict)` returns an `Experiment`.
- user config is normalized into `exp.setup`.
- internal objects are stored in `exp.runtime`, not `exp.setup`.
- base evaluation flow works with `Experiment`.
- ENIGMA and cvc5ml flows work with `Experiment`.
- no new code path relies on broad `**setup` forwarding.

## Open Questions

- Should `db` be considered runtime state or a configured service? Prefer
  runtime for now because it is a live object, even though its provider choices
  are derived from config.
- Should loop counters such as `it` and generated strategies `news` live in
  `Runtime` or in a dedicated loop state object? Prefer `Runtime` initially;
  split later only if loop state grows.
- Should `Experiment` expose convenience properties such as `exp.evals` and
  `exp.options`, or should callers always use `exp.setup.evals`? Prefer a small
  number of convenience properties only where they reduce noise without hiding
  ownership.
