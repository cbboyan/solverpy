"""
Tests for the basic Solver interface.
No solver binary required — only instantiation, property inspection,
command building, and pure-logic methods (valid, solved, simulate).
"""

import pytest
from solverpy.solver.plugins.shell.limits import Limits
from solverpy.solver.shellsolver import ShellSolver


@pytest.fixture
def has_command(solver):
   return isinstance(solver, ShellSolver)


# --- instantiation & identity ---

def test_name_format(solver):
   # Expected: "ClassName:T5"
   name = str(solver)
   assert ":" in name
   classname, limit = name.split(":", 1)
   assert classname
   assert limit.startswith("T")


def test_hash_stable(solver):
   assert hash(solver) == hash(solver)


def test_equality_same_limit(solver):
   other = solver.__class__(solver._limits.limit)
   assert solver == other


def test_inequality_different_limit(solver):
   other = solver.__class__("T999")
   assert solver != other


def test_inequality_other_type(solver):
   assert solver != "not a solver"
   assert solver != 42


# --- status sets ---

def test_statuses_nonempty(solver):
   assert len(solver.statuses) > 0


def test_success_nonempty(solver):
   assert len(solver.success) > 0


def test_timeouts_nonempty(solver):
   assert len(solver.timeouts) > 0


def test_success_subset_of_statuses(solver):
   assert solver.success <= solver.statuses


def test_timeouts_subset_of_statuses(solver):
   assert solver.timeouts <= solver.statuses


def test_success_and_timeouts_disjoint(solver):
   assert solver.success.isdisjoint(solver.timeouts)


# --- valid() ---

def test_valid_good_result(solver):
   status = next(iter(solver.statuses))
   assert solver.valid({"status": status, "runtime": 1.0})


def test_valid_unknown_status(solver):
   assert not solver.valid({"status": "NOTAVALIDSTATUS", "runtime": 1.0})


def test_valid_missing_status_key(solver):
   assert not solver.valid({"runtime": 1.0})


def test_valid_missing_runtime_key(solver):
   status = next(iter(solver.statuses))
   assert not solver.valid({"status": status})


def test_valid_empty(solver):
   assert not solver.valid({})


# --- solved() ---

def test_solved_success_status(solver):
   status = next(iter(solver.success))
   assert solver.solved({"status": status, "runtime": 1.0})


def test_solved_timeout_status(solver):
   status = next(iter(solver.timeouts))
   assert not solver.solved({"status": status, "runtime": 5.0})


def test_solved_all_statuses(solver):
   # Every success status is solved; nothing else is
   for status in solver.statuses:
      result = {"status": status, "runtime": 1.0}
      assert solver.solved(result) == (status in solver.success)


def test_solved_empty(solver):
   assert not solver.solved({})


# --- command() ---

def test_command_is_string(solver, has_command):
   if not has_command:
      pytest.skip("StdinSolver has no command() method")
   assert isinstance(solver.command("problem.p", ""), str)


def test_command_contains_instance(solver, has_command):
   if not has_command:
      pytest.skip("StdinSolver has no command() method")
   assert "my_problem.p" in solver.command("my_problem.p", "")


def test_command_contains_strategy(solver, has_command):
   if not has_command:
      pytest.skip("StdinSolver has no command() method")
   assert "--auto" in solver.command("problem.p", "--auto")


def test_command_contains_limit(solver, has_command):
   if not has_command:
      pytest.skip("StdinSolver has no command() method")
   # The limit string (e.g. "5") should appear in the command
   cmd = solver.command("problem.p", "")
   assert str(solver._limits.timeout) in cmd


# --- simulate() ---

def _solved_result(solver, runtime: float) -> dict:
   status = next(iter(solver.success))
   return {"status": status, "runtime": runtime, "limit": solver._limits.limit}


def _timeout_result(solver, limit: str) -> dict:
   status = next(iter(solver.timeouts - {"TIMEOUT"}))
   return {"status": status, "runtime": float(Limits(limit, {}).timeout), "limit": limit}


def test_simulate_success_within_time(solver):
   result = _solved_result(solver, runtime=1.0)
   simulated = solver.simulate(result)
   assert simulated is not None
   assert simulated["status"] == result["status"]


def test_simulate_success_exceeds_time(solver):
   timeout = solver._limits.timeout
   result = _solved_result(solver, runtime=timeout + 100)
   simulated = solver.simulate(result)
   assert simulated is not None
   assert simulated["status"] == "TIMEOUT"
   assert simulated["runtime"] == timeout


def test_simulate_timeout_tighter_cached_limit(solver):
   # Cached result was a timeout under T1; current solver has T5.
   # T1 < T5 → should recompute (return None).
   solver5 = solver.__class__("T5")
   result = _timeout_result(solver5, limit="T1")
   assert solver5.simulate(result) is None


def test_simulate_timeout_same_limit(solver):
   # Cached timeout at the same limit → no recompute.
   result = _timeout_result(solver, limit=solver._limits.limit)
   assert solver.simulate(result) is not None
