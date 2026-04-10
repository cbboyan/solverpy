# TODO

Migration plan towards `solverpy-grackle` in the solverpy monorepo.

## 1. Remove CVC4

- [x] Delete `grackle/runner/cvc4.py`
- [x] Delete `grackle/trainer/cvc4/`

## 2. Migrate runners to solverpy

Add `grackle/runner/solverpy.py` with `SolverPyRunner(GrackleRunner)` — a generic base
that implements `run()` and `success()` using `self._solver` (a solverpy instance) and
a `RESOURCE_KEY` class attribute.  Subclasses only need to set `self._solver` in
`__init__` and implement `args()`.

Also: replace `PYPROVE_BENCHMARKS` with `SOLVERPY_BENCHMARKS` everywhere; replace
`pyprove:` benchmark prefix in `state.py` with `solverpy:` using `bids.problems()`.

- [x] Add `SolverPyRunner` base class (`grackle/runner/solverpy.py`)
- [x] Refactor `Z3Runner` onto `SolverPyRunner`
- [x] Rewrite `EproverRunner` — use `solverpy.solver.atp.eprover.E`; drop `pyprove` dependency
- [x] Rewrite `LashRunner` — use `solverpy.solver.atp.lash.Lash`
- [x] Rewrite `VampireRunner` — use `solverpy.solver.atp.vampire.Vampire`
- [x] Rewrite `Cvc5Runner` — use `solverpy.solver.smt.cvc5.Cvc5`

## 3. Tests for runners

- [x] `tests/test_runner_eprover.py` — 29 tests: `args()`, `clean()`, `success()`, `run()` with mocked solver
- [x] `tests/test_runner_z3.py` — 28 tests: `args()`, `tactical()`, `success()`, `run()` with mocked solver
- [x] `tests/test_runner_lash.py` — 22 tests
- [x] `tests/test_runner_vampire.py` — 23 tests
- [x] `tests/test_runner_cvc5.py` — 25 tests
- [x] `tests/integration/test_runners.py` — 15 integration tests that invoke real binaries (E, Vampire, Lash, Z3, CVC5); skip if binary not installed; requires `SOLVERPY_BENCHMARKS`

## 4. Migrate trainer domains to GrackleDomain

Use `grackle/trainer/z3/options.py` as the template. Replace raw-string `PARAMS/CONDITIONS/FORBIDDENS` dicts with a proper `GrackleDomain` subclass.

Added `_parse_params`, `_parse_conditions`, `_parse_forbiddens` helpers to `trainer/domain/grackle.py` for parsing legacy raw-string format.
Removed `domains()` overrides from all paramils trainers — they now use the base `ParamilsTrainer.domains()` which calls `self.runner.domain.dump()`.

- [x] Migrate `trainer/lash/domain.py` — `LashDomain(GrackleDomain)`; 16 tests
- [x] Migrate `trainer/vampire/` — `VampireDomain`, `VampireFullDomain`, `VampireCascDomain`; 24 tests
- [x] Migrate `trainer/cvc5/` — `Cvc5BaseDomain`, `Cvc5Domain`; 25 tests
- [x] Migrate `trainer/bitwuzla/domain.py` — `BitwuzlaDomain(GrackleDomain)`; 21 tests
- [x] Rewrite `trainer/eprover/` — new `GrackleDomain` subclasses + `MultiDomain` for staged tuning; 56 tests

## 5. Add RamParILS trainer

Add `grackle/trainer/ramparils.py` as a drop-in alternative to `ParamilsTrainer`:
- Use `ramparils.specialize(strategy, scenario, cache_db, cores)` Python API
- Same interface as `ParamilsTrainer` (`improve(state, conf, insts)`)
- Add `RamparilsStageTrainer` alongside `ParamilsStageTrainer`

- [x] Add `grackle/trainer/ramparils.py` — `RamparilsTrainer`, `RamparilsStageTrainer`
- [x] Add `bin/grackle-ramparils-wrapper.py` — algo wrapper using `#%# RamParIls #%#` result format
- [x] Add `ramparils` to `pyproject.toml` dependencies

## 6. Migrate evaluation to solverpy

Replace the current `Runner.runs()` multiprocessing pool with solverpy's evaluation pipeline
(`solverpy.benchmark.evaluation`).  Evaluation moves from `Runner.runs()` into `main.py`
directly.  The grackle `DB` class is kept but backed by `solverpy_db/` instead of JSON files.

### 6a. `Apply` solverpy plugin + `plugin()` in grackle

Add `Apply(fn: Result -> dict)` to **solverpy** (`solverpy/solver/plugins/apply.py`) — a
generic `Decorator` whose `update()` calls `fn(result)` and merges the returned dict into
`result`.  Useful beyond grackle for any caller wanting to compute and store derived result
keys.  Export from `solverpy/solver/plugins/__init__.py`.

In grackle, add `SolverPyRunner.plugin()` which extracts all needed data as plain
primitives — `penalty` (int), `resource_key` (str|None), `success` (frozenset[str]) — and
returns a single `Apply` instance whose lambda closes only over those primitives (no runner
reference → fully picklable across `multiprocessing` boundaries).  Subclasses override
`plugin()` for custom logic.

Add `SolverPyRunner.setup(solver)` which stores the solver and calls
`solver.init([self.plugin()])` to attach the plugin last (after all built-in plugins
have already populated `status`, `runtime`, etc.).  Concrete runners call `setup()`
instead of assigning `self._solver` directly.

`run()` now reads `result["quality"]` and `result["resources"]` directly from the result
dict instead of computing them inline.

- [x] Add `solverpy/solver/plugins/apply.py` — `Apply(Decorator)` with `fn: Result -> dict`
- [x] Export `Apply` from `solverpy/solver/plugins/__init__.py`
- [x] Add `plugin()` and `setup()` to `SolverPyRunner`
- [x] Update concrete runners to call `setup()` instead of `self._solver = ...`

### 6b. `solverpy_db/confs` and `solverpy_db/strats`

The current `confs/` directory moves into `solverpy_db/confs/`.  A parallel
`solverpy_db/strats/` directory holds the translated solver strategy strings.  Both use the
same SHA224 hash as the filename.  `GrackleRunner.name()` writes to `solverpy_db/confs/`;
`SolverPyRunner` writes the strategy string to `solverpy_db/strats/` when saving a conf.

### 6c. Move evaluation into `main.py`

Remove `Runner.runs()` from `runner.py`.  In `main.py`, replace `db.update(confs)` with a
loop over confs calling `evaluation.run((runner._solver, bid, conf), talker, solverpy_db,
cores)`.  The conf hash serves as `sid`; `bid` comes from the `.fly` config.

### 6d. Use solverpy bids directly in `.fly` config

`trains.data` / `evals.data` are now plain paths passed to `bids.problems()` — same as
solverpy's bid resolution (path relative to `SOLVERPY_BENCHMARKS`; can be a directory or a
file listing problem paths).  Drop the `solverpy:` prefix — it is no longer needed.  Existing
`.fly` files only need the prefix removed; file-list paths continue to work unchanged.

### 6e. Rewrite `DB` to use solverpy_db providers

After each `evaluation.run()` call, populate `DB.results[conf][inst]` by reading back
`{quality, runtime, status, resources}` from solverpy_db.  Remove `DB.save()` / `DB.load()`
(JSON files); persistence is handled by solverpy_db providers.  `DB.update_ranking()`,
`DB.mastered()`, `DB.status()` stay unchanged.

- [ ] Move `confs/` into `solverpy_db/confs/`; write strategy strings to `solverpy_db/strats/`
- [ ] Move evaluation loop from `Runner.runs()` / `DB.update()` into `main.py`
- [ ] Drop `solverpy:` prefix in `state.py:data()`; pass bid directly to `bids.problems()`
- [ ] Rewrite `DB` to read results from solverpy_db providers; remove JSON save/load

## 7. YAML scenario files

- Replace INI-style `.fly` parsing (`tools.py:parse_ini()`) with YAML
- Update `bin/fly-grackle.py` entry point
- Update examples in `examples/`

## 8. Type annotations

Follow solverpy's style (see `~/repos/cbboyan/solverpy/CLAUDE.md`).  Key conventions:
- `Params = dict[str, str]` for solver parameter dicts
- `RunnerConfig(TypedDict, total=False)` for runner config — use `assert "key" in self.config`
  before accessing optional keys (both runtime guard and pyright narrowing)
- `TYPE_CHECKING` guard for heavy imports used only in annotations

### 8a. Runner layer

- [x] Add `grackle/runner/config.py` — `Params` alias + `RunnerConfig(TypedDict, total=False)`
- [x] Annotate `Runner` and `GrackleRunner` in `runner/runner.py`
- [x] Annotate `SolverPyRunner` in `runner/solverpy.py` (also adds `assert "penalty"/"direct" in self.config`)
- [ ] Annotate `runner/lash.py`, `runner/vampire.py`, `runner/z3.py`, `runner/cvc5.py`, `runner/eprover.py`
- [ ] Fix and annotate `runner/stage.py` (broken: missing import, syntax error, wrong delegation pattern)
- [ ] Annotate `runner/bitwuzla.py`, `runner/prover9.py` (legacy; fix pre-existing errors first)

### 8b. Trainer layer

- [ ] Add `grackle/trainer/config.py` — `TrainerConfig(TypedDict, total=False)` with `timeout`,
  `instance_budget`, `restarts`, `log`, `nick`
- [ ] Annotate `trainer/trainer.py`
- [ ] Annotate `trainer/paramils.py`, `trainer/ramparils.py`, `trainer/stage.py`
- [ ] Annotate solver-specific trainers (`lash/`, `vampire/`, `z3/`, `cvc5/`, `eprover/`, `bitwuzla/`)

### 8c. Domain layer

- [ ] Annotate `trainer/domain/grackle.py`, `domain/custom.py`, `domain/multi.py`

### 8d. Core

- [ ] Annotate `db.py`, `jsondb.py`
- [ ] Annotate `state.py`, `main.py`
- [ ] Annotate `tools.py`, `log.py`

## 9. Migrate to solverpy monorepo

- [x] Move package into `~/repos/cbboyan/solverpy` as `packages/solverpy-grackle/`
- [x] Add `pyproject.toml` following `solverpy-learn` pattern (name `solverpy-grackle`, depends on `solverpy` + `PyYAML`)
- [x] Add grackle tests to root `pyproject.toml` testpaths
- [x] Exclude ParamILS Ruby sources, SMAC files, `eprover.old/`, `eprover.newer/`, `examples/`
- [x] Convert `bin/` scripts to proper entry points via `[project.scripts]` — `fly-grackle`, `grackle-paramils`, `grackle-ramparils`; entry point modules in `src/grackle/scripts/`; original scripts kept in `scripts/grackle/`

## 10. Documentation

- Docs will be unified with solverpy's existing `mkdocs` site (same pattern as `solverpy-learn`)
- Add docstrings and integrate into solverpy's `mkdocs-build.sh` / `mkdocs-deploy.sh` workflow
