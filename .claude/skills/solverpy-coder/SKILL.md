---
name: solverpy-coder
description: Use this skill when working on the solverpy codebase. Provides orientation on modules, architecture, coding conventions, the **setup pattern, naming conventions, and known gotchas. Triggers on requests like "explain the codebase", "where do I find ...", "how does X work", "add a new solver", "add a new provider", or any coding task in this repo.
---

# solverpy-coder

Orientation and coding guide for the solverpy codebase.

---

## Package layout

Two packages live under `packages/`:

| Package | Root | Purpose |
|---|---|---|
| `solverpy` | `packages/solverpy/src/solverpy/` | Core solver abstraction, evaluation pipeline, caching |
| `solverpy-learn` | `packages/solverpy-learn/src/solverpy_learn/` | ML model builders, iterative eval/build loop |

Top-level subpackages of `solverpy`:

| Subpackage | Purpose |
|---|---|
| `solver/` | Class hierarchy for solvers; plugin system |
| `solver/atp/` | Concrete ATP solvers: E, Vampire, Prover9, Lash |
| `solver/smt/` | Concrete SMT solvers: CVC5, Z3, Bitwuzla |
| `solver/plugins/` | Decorator and Translator plugins |
| `solver/plugins/shell/` | Limits, Time, Timeout, Memory plugins |
| `solver/plugins/status/` | Tptp, Smt, Limiter status-parsing plugins |
| `solver/plugins/db/` | Bid, Sid, Outputs, Errors — DB translation plugins |
| `benchmark/` | Evaluation orchestration, result caching, reporting |
| `benchmark/path/` | `bids` — problem list resolution; `sids` — strategy file resolution |
| `benchmark/db/` | Abstract and concrete database providers (JSON, solved, status, outputs) |
| `task/` | Multiprocessing task execution; talker progress reporters |
| `setups/` | High-level `Setup` TypedDict and helper functions (eprover, cvc5, …) |
| `tools/` | Utilities: logging, timing, patterns, markdown/PlantUML, typing aliases |

Top-level subpackages of `solverpy_learn`:

| Subpackage | Purpose |
|---|---|
| `builder/` | `Builder` base class; `EnigmaModel`, `EnigmaSel`, `EnigmaGen`, `Enigma`, `Cvc5MlBuilder`, `SVM` |
| `builder/autotune/` | Optuna-based hyperparameter tuning |
| `builder/plugins/` | Training data extraction as solver plugins |
| `setups/` | ML-specific Setup helpers, iterative loop orchestration |

---

## Core concepts

### bid and sid

- **bid** (benchmark id) — a string path to a problem set, resolved relative to `SOLVERPY_BENCHMARKS` (default cwd). Can be a directory (all files inside) or a text file listing one problem path per line.
- **sid** (strategy id) — a filename inside `solverpy_db/strats/`. Contains raw solver CLI options. Parametric sids use `base_sid@var=val:var2=val2` notation; variable slots in the file use `@@@ var : default @@@` syntax.

### Result

`Result = dict[str, Any]` — always contains at least:
- `status: str` — e.g. `"Theorem"`, `"sat"`, `"TIMEOUT"`, `"unknown"`
- `runtime: float` — seconds

Additional keys depend on plugins (e.g. `limit`, training data, output path).

### Setup TypedDict

`Setup` (`setups/setup.py`) is a `TypedDict(total=False)` — a plain dict with documented optional keys. It is the central experiment configuration, threaded through the entire codebase.

Common keys:

| Key | Type | Meaning |
|---|---|---|
| `limit` | `str` | Resource limit, e.g. `"T10"` (10 s) or `"T10-M1024"` (10 s, 1 GB) |
| `bidlist` | `list[str]` | Benchmark ids to evaluate |
| `sidlist` | `list[str]` | Strategy ids to evaluate |
| `cores` | `int` | Parallel worker count (default 4) |
| `solver` | `SolverPy` | Instantiated solver (set by `setups.eprover()` etc.) |
| `db` | `DB` | Database instance (set by `setups.evaluation()`) |
| `builder` | `Builder` | ML model builder (set by solverpy_learn setups) |
| `plugins` | `list[Plugin]` | Extra plugins (Bid, Sid always added by `init()`) |
| `static` | `list[str]` | Fixed solver CLI options |
| `binary` | `str` | Override solver binary path |
| `options` | `list[str]` | Feature flags: `"flatten"`, `"compress"`, `"outputs"`, `"no-flatten"`, … |
| `complete` | `bool` | Count SAT as success (for incomplete solvers) |
| `ref` | `bool\|int\|str` | Reference strategy for reporting |
| `loops` | `int` | ML loop iterations |
| `force` | `bool` | Recompute even if cached |

---

## The `**setup` pattern

Setup is passed by **unpacking** (`**setup`) into functions, not as a single argument. This keeps every function signature self-documenting and allows ignoring irrelevant keys.

```python
# In setups/loop.py
def launch(setup, devels=None):
    ...
    evaluator.launch(**setup)      # all setup keys become kwargs

# In benchmark/evaluation.py
def launch(solver, bidlist, sidlist, ref=True, cores=4, talker=None, **others):
    ...  # only takes what it needs; **others absorbs the rest
```

Rules:
- Add `**kwargs` (or `**others`) to any function that only needs some setup keys.
- Never pass `setup` as a positional argument into deep utilities — unpack it.
- Add new top-level config keys to `Setup` in `setups/setup.py` with a comment.

---

## Fully qualified name conventions

The module hierarchy doubles as a readable description of what a function does. Examples:

| Fully qualified name | What it does |
|---|---|
| `solverpy.setups.eprover` | configure solver setup for E Prover |
| `solverpy.setups.evaluation` | configure setup for benchmark evaluation |
| `solverpy.setups.launch` | launch evaluation from a setup dict |
| `solverpy.benchmark.evaluation.run` | run one (solver, bid, sid) evaluation job |
| `solverpy.benchmark.evaluation.launch` | run all (solver, bid, sid) combinations |
| `solverpy.benchmark.path.bids.problems` | get problem list from a bid |
| `solverpy.benchmark.path.sids.load` | load strategy definition for a sid |
| `solverpy.benchmark.db.db.DB.query` | query cached results for a task list |
| `solverpy.task.launcher.launch` | run tasks in parallel via multiprocessing |
| `solverpy_learn.setups.loop.launch` | run the iterative ML eval/build loop |
| `solverpy_learn.builder.enigma.Enigma.build` | train ENIGMA ML model |
| `solverpy_learn.builder.enigma.solo` | generate a solo-guidance strategy |
| `solverpy_learn.builder.enigma.coop` | generate a coop-guidance strategy |

When naming new functions or modules, follow the same pattern: each segment narrows the domain, the final segment is a verb or noun describing the action/object.

---

## Solver class hierarchy

```
SolverPyObj          object.py       root: repr + YAML serialization
  └─ Solver          solver.py       abstract: solve(), run(), process()
       └─ PluginSolver pluginsolver  adds Plugin registry (decorators + translators)
            └─ SolverPy solverpy.py  adds resource limits + result simulation
                 ├─ ShellSolver      subprocess execution (most solvers)
                 │    ├─ E, Vampire, Prover9, Lash   (atp/)
                 │    └─ Cvc5, Z3, Bitwuzla          (smt/)
                 └─ StdinSolver      stdin-fed subprocess
                 └─ Reloader         replay from cached outputs
```

`solve()` chains: translate → run/command → process → update → finished.

---

## Plugin system

Two plugin roles:

| Role | Base class | Registers on | Called during |
|---|---|---|---|
| `Decorator` | `decorator.py` | `solver.decorators` | `decorate(cmd)` — wraps command; `update()` — post-processes result |
| `Translator` | `translator.py` | `solver.translators` | `translate(instance, strategy)` — transforms inputs |

Built-in plugins (added automatically by `setups.init()`):
- `Bid` — translates `(bid, problem)` → full file path
- `Sid` — translates `sid` → strategy definition string (+ parametric expansion)
- `Outputs` / `Errors` — store raw solver output (added when `"outputs"` in options)

Resource plugins (added by `ShellSolver.__init__` via `Limits`):
- `Limits` — registers as both Decorator (appends CLI flags) and Translator (prepends to strategy) depending on `cmdline` flag
- `Time` — adds `runtime` to result
- `Timeout` — wraps command with `timeout` utility
- `Memory` — wraps command with memory limit
- `Limiter` — maps non-zero exit codes to timeout status (always added by `SolverPy`)

Status plugins (added by concrete solver subclasses):
- `Tptp` — parses TPTP status line; populates `solver.success/timeouts/statuses`
- `Smt` — parses SMT status; populates same properties

Call a plugin method by id (used to disable training data collection per task):
```python
solver.call(pid, "disable")          # call plugin.disable()
solver.call(pid, "enable")
```

---

## Database providers

Providers implement the cache layer under `solverpy_db/`. Each provider handles one output type:

| Provider | Directory | Content |
|---|---|---|
| `Jsons` | `results/` | `{problem: result}` JSON dict (gzip), one file per (sid, bid) |
| `Solved` | `solved/` | Newline-separated solved problem names |
| `Status` | `status/` | Tab-separated `problem\tstatus` lines |
| `Outputs` | `outputs/` | Raw solver stdout, one file per problem |
| `Errors` | `errors/` | Solver stderr, one file per problem |

`Jsons.query()` calls `solver.simulate(cached_result)` — this can return `None` (force recompute) or a synthetic result (simulate timeout at a lower limit). This is the key mechanism that allows evaluation under different time limits without re-running.

---

## Result simulation

`SolverPy.simulate(result)` is called by `Jsons.query()` when a cached result exists:

- **Cached success, runtime ≤ new timeout** → return result as-is ✓
- **Cached success, runtime > new timeout** → return synthetic timeout result ✓
- **Cached timeout, old limit < new limit** → return `None` (trigger recompute) ✓
- **Cached timeout, old limit ≥ new limit** → return cached result as-is ✓

The cached result must contain `limit` for simulation to work. The `Jsons` provider stores the limit with each result.

---

## Coding conventions

**Indent**: 3 spaces (configured in `pyproject.toml` via `yapf`). Format with `yapf -i <file>`.

**Imports**: standard library first, then package-relative. Avoid star imports.

**`**kwargs` forwarding**: every class in the hierarchy passes `**kwargs` up:
```python
def __init__(self, myarg, **kwargs):
    super().__init__(**kwargs)
    self.myarg = myarg
```

**`SolverPyObj` repr**: pass all constructor args as keyword arguments to `super().__init__()` if you want them included in `repr`:
```python
class Foo(SolverPyObj):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)   # will appear in repr: Foo(x=1,y=2)
```

**Plugin id**: give plugins a string id when they need to be called remotely:
```python
plugin = MyPlugin(pid="mykey")
solver.call("mykey", "disable")
```

**Options list**: use a list of strings, not a flags dict. Negate with `"no-"` prefix. Check presence with `"flatten" in setup["options"]`.

**Limit strings**: always start with `T` (timeout). Memory is `M`. The `Limits` class parses `-T10-M1024` style strings. The `builder` dict maps flag letters to command line templates.

---

## Common gotchas

### `Limits` is both Decorator and Translator
`Limits` in `solver/plugins/shell/limits.py` inherits from both `Decorator` and `Translator`. Its `cmdline` constructor parameter decides which role it takes: `cmdline=True` → registers as decorator (appends to command); `cmdline=False` → registers as translator (prepends to strategy string).

### Solver equality is string-based
`SolverPy.__eq__` and `__hash__` compare `str(self)`. Two solver instances with the same string representation are considered identical. This matters when solvers are used as dict keys (e.g., in job result maps).

### Setup is mutated in place
`setups.eprover(setup)` and similar functions modify `setup` in place and also return it. The return value is the same object. Do not assume it creates a copy.

### `total=False` means all keys are optional
`Setup` is `TypedDict(total=False)`. Type checkers will not warn if you forget a required key. Always check for `None` / missing before use.

### Multiprocessing requires picklability
`SolverTask` is executed in a `multiprocessing` pool with spawn context. All objects stored in the task (solver, plugins, etc.) must be picklable. Closures and lambdas are not picklable — use named functions or classes.

### Plugin order matters
Decorators and translators are applied in registration order. `Bid` must run before `Sid` because `Bid` translates `(bid, problem)` → file path, which `Sid` may depend on. `init()` in `setups/common.py` registers them in the correct order — match it when adding plugins manually.

### Parametric sid expansion
`sids.load(sid)` handles `base@var=val` notation. If you pass a plain sid with no `@`, it loads the file directly. The `@@@ var : default @@@` placeholders in strategy files are only expanded when args are provided via `sids.instantiate(strategy, args)`.

### `simulate()` requires `limit` in the cached result
If a cached result lacks the `limit` key, `simulate()` may fall back to a conservative behavior or raise. The `Jsons` provider injects this key automatically; manual result dicts must include it for simulation to work correctly.

### `SolverTask.instance` is a tuple
`task.instance == (bid, problem)` — a tuple, not just the problem path. The `Bid` translator plugin unwraps it into a full file path. Solvers that receive `instance` directly (outside the plugin chain) must handle this tuple.

### Training data is a plugin
In `solverpy_learn`, training data collection (`trains`) is implemented as a solver plugin that can be enabled and disabled per-task via `solver.call("trains", "disable")`. It hooks into the `update()` lifecycle to extract proofs after each solve.

### ML loop iterates one past the last training step
`oneloop()` skips the model build on the final iteration — evaluation happens, training data is collected, but `builder.build()` is not called. This is intentional: the loop is structured as *evaluate → build → evaluate → build → … → evaluate* (n evaluations, n-1 builds for n loops).

---

## Adding a new solver

1. Create `solver/atp/mysolver.py` (or `solver/smt/`) subclassing `ShellSolver`.
2. Set `_binary = "mysolver"` class variable.
3. In `__init__`, call `super().__init__(cmd, limit, builder, plugins=[Tptp(), ...], **kwargs)`.
4. Override `process(output) → Result` if the output format is non-standard.
5. Add `mysolver()` to `setups/solver.py` following the same pattern as `eprover()`.
6. Expose via `setups/__init__.py` if needed.

## Adding a new DB provider

1. Subclass `CachedProvider` in `benchmark/db/providers/myprovider.py`.
2. Implement `query(task) → Result|None` and `store(task, result) → None`.
3. Override `path(bid, sid, limit) → str` for the file path.
4. Add `MyProvider.Maker` factory to the provider list in your `evaluation()` setup call.
