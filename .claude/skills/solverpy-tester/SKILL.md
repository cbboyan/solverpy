---
name: solverpy-tester
description: Use this skill when writing, extending, or debugging tests in the solverpy codebase. Triggers on requests like "add a test", "write a test for X", "run tests", "add benchmark evaluation test", "test a new solver", or any task involving pytest in this repo.
---

# solverpy-tester

Guide for writing and extending tests in the solverpy codebase.

---

## Test layout

```
tests/
├── data/
│   ├── problems/          # benchmark problem sets (subdirs, 10 problems each)
│   │   ├── bushy010/      # TPTP problems for ATP solvers
│   │   ├── smt010/        # SMT-LIB2 problems for CVC5/Z3
│   │   └── sage010/       # SMT-LIB2 problems for Bitwuzla
│   └── solverpy_db/
│       └── strats/        # strategy files (one per solver variant)
│           ├── eprover-default
│           ├── vampire-default
│           ├── cvc5-enum
│           └── bitwuzla-default   # empty file = no extra flags
└── test_benchmark_eval.py  # parametrised end-to-end evaluation tests
```

---

## Running tests

```bash
# All fast tests (omit slow)
pytest

# A single parametrised case
pytest tests/test_benchmark_eval.py -k bitwuzla-sage010-default

# Include slow-marked tests
pytest -m slow

# Run all (fast + slow)
pytest -m ""
```

Use `pytest` (not `python -m pytest`).

No env vars needed — the `solverpy_env` fixture sets `SOLVERPY_BENCHMARKS` and
`SOLVERPY_DB` automatically before each module run.

---

## Benchmark evaluation test pattern

All end-to-end solver tests live in `tests/test_benchmark_eval.py` as entries in
`EVAL_CASES`.  Each entry is a `pytest.param` with `(solver_fn, bidlist, sidlist)`:

```python
EVAL_CASES = [
    pytest.param(
        (setups.bitwuzla, ["sage010"], ["bitwuzla-default"]),
        id="bitwuzla-sage010-default",
        marks=pytest.mark.slow,   # omit if fast enough
    ),
    ...
]
```

The `eval_case` fixture runs the full pipeline and returns `(setup, bid, sid)`.
All other fixtures (`db_results`, `db_solved`, `db_status`, …) derive from it.

### Tests that are checked for each case

| Test | What it checks |
|---|---|
| `test_results_file_exists` | gzip JSON result file written |
| `test_outputs_plus_errors_count` | output + error files = 10 (problem count) |
| `test_results_all_have_status` | every result has `"status"` key |
| `test_results_all_have_runtime` | every result has `"runtime"` key |
| `test_solved_file_exists` | solved list file written |
| `test_solved_nonempty` | at least one problem solved |
| `test_solved_subset_of_results` | solved names ⊆ result keys |
| `test_status_count` | status entries = result entries |
| `test_status_values_valid` | every status is in `solver._statuses` |

---

## Checklist: adding a new solver evaluation case

1. **Problem set** — add 10 problems to `tests/data/problems/<name>010/`.
2. **Strategy file** — create `tests/data/solverpy_db/strats/<solver>-<variant>`.
   - Can be empty (no extra CLI flags).
3. **`EVAL_CASES` entry** — add a `pytest.param` in `test_benchmark_eval.py`.
4. **`slow` mark** — add `marks=pytest.mark.slow` for any case that takes > ~5 s.
5. **Verify `setups.<solver>()`** — check that the corresponding setup function in
   `packages/solverpy/src/solverpy/setups/solver.py` initialises all required keys
   (see *Setup function gotchas* below).

---

## Setup function gotchas

Every `setups.<solver>()` function must call `default(setup, "static", ...)` before
`init(setup)`.  Missing this causes `AssertionError: "static" not in setup` at runtime.

Correct pattern (mirrors `z3()` and `cvc5()`):

```python
def bitwuzla(setup: Setup) -> Setup:
    default(setup, "static", "")   # ← required; empty string = no flags
    init(setup)
    return solver(setup, Bitwuzla)
```

---

## `valid_statuses` fixture — use `_statuses`, not `_success | _timeouts`

The `valid_statuses` fixture must return `solver._statuses` (the full set), **not**
`solver._success | solver._timeouts`.

- `_success` — statuses that count as solved (e.g. `sat`, `unsat`, `Theorem`)
- `_timeouts` — statuses that count as timeout (e.g. `TIMEOUT`, `memout`)
- `_statuses` — all known statuses including `_success`, `_timeouts`, **and**
  `SMT_FAILED` / `TPTP_FAILED` (e.g. `unknown`, `CounterSatisfiable`)

SMT solvers (Bitwuzla, CVC5, Z3) legitimately return `unknown` for problems they
cannot solve within the time limit.  This is `SMT_FAILED`, not a timeout, so it
is in `_statuses` but not in `_success | _timeouts`.

```python
@pytest.fixture(scope="module")
def valid_statuses(eval_case):
    setup, _, _ = eval_case
    solver = setup["solver"]
    return solver._statuses   # ← correct; includes 'unknown', 'CounterSatisfiable', …
```

---

## `slow` mark registration

The `slow` mark must be registered in `pyproject.toml` to avoid `PytestUnknownMarkWarning`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = ["slow: marks tests as slow (skipped by default)"]
```

To skip slow tests by default, add this `addopts` line (opt-in if desired):

```toml
addopts = "-m 'not slow'"
```

Currently slow tests are only excluded when explicitly deselected with `-m`.

---

## Environment variables

| Variable | Value for tests | Purpose |
|---|---|---|
| `SOLVERPY_BENCHMARKS` | `tests/data/problems` | Root for bid resolution |
| `SOLVERPY_DB` | `tests/data/solverpy_db` | Where results, strats, solved, etc. live |

Both must be set before running evaluation tests.  The `solverpy_env` fixture also
clears cached DB subdirs (except `strats/`) and flushes the bid cache before each
module run.
