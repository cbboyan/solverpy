"""
Tests that actually launch the solver binary.
Requires the solver binary to be installed and in PATH.
Tests are skipped automatically if the binary is not found.
"""

import pytest
from pathlib import Path

AGATHA = Path(__file__).parent / "data" / "agatha.p"
STRATEGY = ""  # default strategy: no extra options


@pytest.fixture(autouse=True)
def require_binary(solver):
   if not solver.isinstalled():
      pytest.skip(f"solver binary not found: {solver._binary}")


_cache: dict = {}


@pytest.fixture
def agatha_output(solver):
   key = f"{solver}:run"
   if key not in _cache:
      _cache[key] = solver.run(str(AGATHA), STRATEGY)
   return _cache[key]


@pytest.fixture
def agatha_result(solver):
   key = f"{solver}:solve"
   if key not in _cache:
      _cache[key] = solver.solve(str(AGATHA), STRATEGY)
   return _cache[key]


# --- run() ---

def test_run_returns_string(agatha_output):
   assert isinstance(agatha_output, str)


def test_run_nonempty(agatha_output):
   assert len(agatha_output) > 0


def test_run_contains_instance(agatha_output):
   assert "agatha" in agatha_output.lower()


# --- solve() ---

def test_solve_returns_dict(agatha_result):
   assert isinstance(agatha_result, dict)


def test_solve_has_status(agatha_result):
   assert "status" in agatha_result


def test_solve_has_runtime(agatha_result):
   assert "runtime" in agatha_result
   assert isinstance(agatha_result["runtime"], float)
   assert agatha_result["runtime"] >= 0.0


def test_solve_valid_result(solver, agatha_result):
   assert solver.valid(agatha_result)


def test_solve_status_in_statuses(solver, agatha_result):
   assert agatha_result["status"] in solver.statuses


def test_solve_agatha_solved(solver, agatha_result):
   # agatha.p is a Theorem — any complete prover must solve it within T1
   assert solver.solved(agatha_result)


def test_solve_agatha_theorem(agatha_result):
   assert agatha_result["status"] == "Theorem"


def test_solve_runtime_within_limit(solver, agatha_result):
   assert agatha_result["runtime"] <= solver._limits.timeout + 1  # +1 for system overhead
