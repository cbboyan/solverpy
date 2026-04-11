# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Location

This package lives in the solverpy monorepo at `~/repos/cbboyan/solverpy/packages/solverpy-grackle/`.
The source root is `src/solverpy_grackle/`. The original standalone repo is at `~/repos/cbboyan/grackle` (kept for reference).

Remaining planned work:
- **YAML scenario files**: migrate `.fly` config format from INI-style to YAML
- **Type annotations**: add type hints throughout (follow solverpy's style — see its `CLAUDE.md`)
- **Docs**: generate documentation (follow solverpy's `mkdocs` setup)

## What is Grackle

Grackle is an automated system for inventing a portfolio of **good-performing and complementary configurations** of a parametrized algorithm (e.g., a theorem prover or SMT solver). It iterates between:
1. **Evaluation**: Running all known configurations on benchmark problems
2. **Selection**: Picking the best candidate for improvement
3. **Training**: Using ParamILS (or RamParILS) to tune parameters and invent a new configuration

## Installation (developer mode)

```bash
export PATH=$PATH:$PWD/bin
pip install -e .
```

## Running

```bash
fly-grackle.py grackle.fly
```

See `examples/lash/` and `examples/vampire/` for complete example setups.

## Architecture Overview

### Core Loop (`solverpy_grackle/main.py`, `solverpy_grackle/state.py`)

The main loop in `main.py` calls `evaluate()` → `reduction()` → `select()` → `improve()` each iteration. `state.py` manages all shared state: the strategy collection, evaluation databases, runner/trainer instances, and genealogy tracking.

Configuration is loaded from `.fly` files (INI-style) via `solverpy_grackle/tools.py:parse_ini()`. Classes are instantiated dynamically via fully-qualified Python paths (e.g., `solverpy_grackle.runner.lash.LashRunner`).

### Runner System (`solverpy_grackle/runner/`)

Two-level hierarchy:
- **`Runner`** (base): abstract `cmd()`, `process()`, `success()` interface + subprocess execution and parallel `runs()` via multiprocessing pool
- **`GrackleRunner`** (extends Runner): adds configuration file management (`confs/` directory), SHA224-based config naming, parameter parsing/cleaning, and domain (parameter space) loading

Solver-specific runners extend `GrackleRunner`:
- `Z3Runner` — Z3 SMT solver — **the reference implementation**, uses `solverpy`
- `LashRunner` — LASH ATP prover
- `VampireRunner` — Vampire ATP
- `EproverRunner` — E-Prover ATP (**outdated**: depends on `pyprove.eprover`)
- `Cvc5Runner` — CVC5 SMT solver
- `BitwuzlaRunner`, `Prover9Runner`, `Cvc4Runner` — less maintained

**All new and updated runners must use `solverpy`** (see `solverpy_grackle/runner/z3.py` as the template). The `solverpy` library lives at `~/repos/cbboyan/solverpy` (see its `CLAUDE.md` for full details) and provides solver classes for all supported provers: `solverpy.solver.atp.{lash,vampire,eprover,prover9}` and `solverpy.solver.smt.{z3,cvc5,bitwuzla}`.

The `solverpy` solver hierarchy is: `Solver → PluginSolver → SolverPy → ShellSolver → {E, Vampire, Lash, Prover9, Cvc5, Bitwuzla}` (Z3 uses `StdinSolver` instead of `ShellSolver`). Solvers are instantiated with a limit string (e.g., `"T10"` for 10s, `"T10-M4"` for 10s+4GB) and optional `static` args override. `ShellSolver.solve(instance, strategy)` runs `{time} {cmd} {strategy} {instance}` as a subprocess.

Note: grackle uses `SOLVERPY_BENCHMARKS` to resolve benchmark paths (same as solverpy). The old `PYPROVE_BENCHMARKS` variable has been fully removed.

The `solverpy` pattern replaces `cmd()` + `process()` with a single overridden `run()`:

```python
# __init__: instantiate the solverpy solver
self._solver = SolverClass(limit=f"T{timeout}", ...)

# run(): call solve(), check valid/solved, extract result
def run(self, entity, inst):
    params = entity if self.config["direct"] else self.recall(entity)
    strat = self.args(params)  # build strategy string
    problem = os.path.join(os.getenv("SOLVERPY_BENCHMARKS", "."), inst)
    try:
        result = self._solver.solve(problem, strat)
    except Exception:
        result = {}
    if not self._solver.valid(result):
        ...  # log and return None
    ok = self._solver.solved(result)
    status = result["status"]
    runtime = result["runtime"]  # set by solverpy Time plugin (realtime - systime)
    quality = 10+int(1000*runtime) if ok else self.config["penalty"]
    resources = result.get("<solver-specific-key>", -1)
    return [quality, runtime, status, resources]

def success(self, result):  # result is a status string
    return result in self._solver.success
```

The `solverpy` solver's `solve(instance, strategy)` runs `{cmd} {strategy} {instance}` (strategy is appended between the static args and the problem file). The result dict always has `status` (from the status plugin) and `runtime` (from the `Time` plugin, computed as `realtime - systime`). Solver-specific resource keys vary: LASH → `Steps`, Vampire → `Active`, E → `Processed`, CVC5 → `resource::resourceUnitsUsed`.

### Trainer System (`solverpy_grackle/trainer/`)

- **`Trainer`** (base): abstract `improve(state, conf, insts)` → new conf name
- **`ParamilsTrainer`**: main trainer — calls `self.runner.domain.dump()` to get the ParamILS param spec, invokes `reparamils.launch()` (Ruby script `paramils/param_ils_2_3_run.rb`), returns best params
- **`RamparilsTrainer`** *(planned)*: replacement/alternative to `ParamilsTrainer` using **RamParILS** (`~/repos/cbboyan/ramparils`) — a parallel Rust rewrite of ParamILS with a native Python API (`pip install ramparils`). Key advantages: parallel `(config, instance)` evaluation, persistent SQLite result cache, no Ruby subprocess. API: `ramparils.specialize(strategy, scenario, cache_db, cores)` → `dict[str,str]`. The scenario dict uses the same `paramfile` format as ParamILS. Should be added as a drop-in alternative alongside the existing `ParamilsTrainer`.
- **`Smac3Trainer`**: alternative using SMAC3 (**outdated**: uses SMAC v1 API `smac.facade.smac_ac_facade.SMAC4AC` which no longer exists in current SMAC)
- **`StageTrainer`** / **`ParamilsStageTrainer`**: wraps ParamilsTrainer for multi-domain staged tuning — requires `runner.domain` to be a `MultiDomain`; temporarily swaps `runner.domain` to each sub-domain per stage

Solver-specific trainers live in subdirectories (`trainer/lash/`, `trainer/vampire/`, `trainer/z3/`, etc.) and primarily define the parameter domain.

### Domain System (`solverpy_grackle/trainer/domain/`)

Each solver needs a domain definition:
- **`GrackleDomain`** (base): defines `params` (name→range/set), `defaults`, `conditions` (parameter dependencies), `forbiddens`. `dump()` exports to ParamILS `.pcs` format.
- **`CustomDomain`**: programmatic builder with `add_param()` / `add_dep()`
- **`MultiDomain`**: combines multiple domains for staged tuning via `join()`/`split()`

**All new and updated domains must subclass `GrackleDomain`** (or `CustomDomain`). Z3 is the reference implementation: `OptionsDomain` (`trainer/z3/options.py`) extends `GrackleDomain` directly; `TacticsDomain` (`trainer/z3/tactics.py`) extends `CustomDomain`. `ParamilsTrainer` accesses the domain only through `self.runner.domain.dump()`.

**State of trainer domains** — what still needs migration to `GrackleDomain`:

| Solver | Trainer | Domain type | Status |
|--------|---------|-------------|--------|
| Z3 | `ParamilsTrainer` (via runner) | `OptionsDomain(GrackleDomain)`, `TacticsDomain(CustomDomain)` | **Reference** |
| Bitwuzla | `BitwuzlaParamilsTrainer` | Runner uses `DefaultDomain(GrackleDomain)`; trainer also has a raw-string `domain.py` | Partially migrated |
| LASH | `LashParamilsTrainer` | Raw-string `PARAMS/CONDITIONS/FORBIDDENS` — not a GrackleDomain subclass | Needs migration |
| Vampire | `VampireParamilsTrainer` (+ Full/Casc variants) | Raw-string, multiple variants (`domain.py`, `domain_full.py`, `domain_casc.py`) | Needs migration |
| CVC5 | `Cvc5ParamilsTrainer` | Raw-string, multiple variants (`domain_base/regular/uf/all/domain.py`) | Needs migration |
| CVC4 | `Cvc4ParamilsTrainer` | Raw-string `PARAMS/CONDITIONS/FORBIDDENS` | **Obsolete — mark for removal** |
| EProver | `EproverParamilsTunerTrainer` | Tuner-managed, non-standard architecture | Needs rewrite; use `MultiDomain` for staged tuning |

### Database (`solverpy_grackle/db.py`, `solverpy_grackle/jsondb.py`)

`db.py` tracks `results[conf][inst] = [quality, runtime, status, ...]` and `ranking[inst] = [conf, ...]` sorted by quality. `jsondb.py` adds JSON serialization, portfolio scoring, and greedy portfolio selection.

On restart, rename `db-trains-init.json` → `db-trains-cache.json` to reuse initial strategy evaluations.

## Key Design Patterns

**Config naming**: Configurations are identified by `SHA224(params_string)` and stored as files in `confs/`. The prefix is runner-specific (e.g., `lash-`, `eprover-`).

**Direct vs. indirect mode**: When `runner.config["direct"] = True` (default), strategy params are passed directly as a string to the solver. When `False`, a conf name (sid) is passed and the strategy is loaded from file. In the planned solverpy-based evaluation, this maps directly to the presence or absence of solverpy's `Sid` translator plugin (`solverpy.solver.plugins.db.sid.Sid`): with `Sid`, the solver receives a sid and loads the strategy from `solverpy_db/strats/`; without it, the strategy string is passed directly.

**Domain loading in runners**: `GrackleRunner.__init__` calls `load_domain(cfg)` which reads `domain.*` keys from the runner config to instantiate the domain class dynamically.

**Attention tracking**: `state.attention[inst]` counts how many times an instance has been used for training. Selection heuristics use this to diversify training targets.

**Genealogy**: `state.elders[conf]` maps each invented config back to its initial strategy. `state.nicks` gives human-readable names (`s00`, `i001s00`, etc.).

## Outdated Components

- **`EproverRunner`** (`runner/eprover.py`): depends on `pyprove.eprover` and `pyprove.expres` — needs rewrite to use `solverpy.solver.atp.eprover.E`
- **`LashRunner`**, **`VampireRunner`**, **`Cvc5Runner`**: functional but not yet migrated to `solverpy` — need rewrite following the Z3Runner pattern
- **`Smac3Trainer`** (`trainer/smac3.py`): uses old SMAC v1 API (`SMAC4AC`, `Scenario`) that has been replaced in current SMAC versions
- **CVC4** (`runner/cvc4.py`, `trainer/cvc4/`): **obsolete — mark for removal**

## `.fly` Configuration Reference

```ini
cores = 56          # CPU count
tops = 50           # Max strategies in active portfolio
best = 3            # Min instances mastered to survive reduction
rank = 1            # Top-N strategies per instance count as "mastering" it
inits = greedy15    # File listing initial strategy filenames
timeout = 86400     # Overall wall-clock limit (seconds)
atavistic = False   # True = all strategies compete; False = active only
selection = default # Heuristic: default|weak|random|mul|div|reverse|family (combinable with +)

runner.prefix = lash-             # Prefix for generated config filenames

trains.data = problems.ok         # Benchmark instance list file
trains.runner = solverpy_grackle.runner.lash.LashRunner
trains.runner.timeout = 1

trainer = solverpy_grackle.trainer.lash.paramils.LashParamilsTrainer
trainer.runner = solverpy_grackle.runner.lash.LashRunner
trainer.runner.timeout = 1
trainer.timeout = 300
trainer.restarts = True
```

`evals.*` (optional) defines a separate evaluation set; `runner.*` sets defaults shared by all runners.
