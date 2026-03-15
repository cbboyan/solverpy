"""
Tests that actually launch the solver binary.
Requires the solver binary to be installed and in PATH.
Tests are skipped automatically if the binary is not found.
"""

import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def require_binary(case):
   solver = case[0]
   if not solver.isinstalled():
      pytest.skip(f"solver binary not found: {solver._binary}")


_cache: dict = {}


@pytest.fixture
def solver(case):
   return case[0]


@pytest.fixture
def problem(case):
   return case[1]


@pytest.fixture
def strategy(case):
   return case[2]


@pytest.fixture
def expected_status(case):
   return case[3]


@pytest.fixture
def output(case):
   solver, problem, strategy, _ = case
   key = f"{solver}:{solver._binary}:{problem}:run"
   if key not in _cache:
      _cache[key] = solver.run(problem, strategy)
   return _cache[key]


@pytest.fixture
def result(case):
   solver, problem, strategy, _ = case
   key = f"{solver}:{solver._binary}:{problem}:solve"
   if key not in _cache:
      _cache[key] = solver.solve(problem, strategy)
   return _cache[key]


# --- run() ---

def test_run_returns_string(output):
   assert isinstance(output, str)


def test_run_nonempty(output):
   assert len(output) > 0


def test_run_contains_instance(problem, output):
   assert Path(problem).stem in output.lower()


# --- solve() ---

def test_solve_returns_dict(result):
   assert isinstance(result, dict)


def test_solve_has_status(result):
   assert "status" in result


def test_solve_has_runtime(result):
   assert "runtime" in result
   assert isinstance(result["runtime"], float)
   assert result["runtime"] >= 0.0


def test_solve_valid_result(solver, result):
   assert solver.valid(result)


def test_solve_status_in_statuses(solver, result):
   assert result["status"] in solver.statuses


def test_solve_solved(solver, result):
   assert solver.solved(result)


def test_solve_expected_status(result, expected_status):
   assert result["status"] == expected_status


def test_solve_runtime_within_limit(solver, result):
   assert result["runtime"] <= solver._limits.timeout + 1  # +1 for system overhead
