"""
Tests for Z3Runner.
No Z3 binary required — covers args(), success(), and run()
with a mocked solverpy solver.
"""

import pytest
from unittest.mock import MagicMock, patch

from grackle.runner.z3 import Z3Runner, tactical
from grackle.trainer.z3.options import OptionsDomain
from grackle.trainer.z3.tactics import TACTICS, BOOLS, DEPTHS


# --- fixtures ---

def _mock_load_domain(self, cfg):
   self._domain = OptionsDomain()
   self._conds = {}


@pytest.fixture
def runner():
   with patch("grackle.runner.z3.Z3"), \
        patch("grackle.runner.runner.GrackleRunner.load_domain", _mock_load_domain):
      r = Z3Runner({"timeout": 10})
   return r


# minimal params that trigger a single tactic (simplify = index 0)
def _tactic_params(tactic_idx=0):
   params = {"t__count": "1", "t__t0": str(tactic_idx)}
   # add bool/depth args for the tactic if needed
   name = TACTICS[tactic_idx]
   for j, arg in enumerate(BOOLS.get(name, [])):
      params[f"t__t0__bool{j}"] = "false"
   for j, arg in enumerate(DEPTHS.get(name, [])):
      params[f"t__t0__depth{j}"] = "1024"
   return params


# --- args() — options only ---

def test_args_empty_params_returns_empty(runner):
   result = runner.args({})
   assert result.strip() == ""


def test_args_single_option(runner):
   result = runner.args({"smt.mbqi": "true"})
   assert "(set-option :smt.mbqi true)" in result


def test_args_multiple_options(runner):
   params = {"smt.mbqi": "true", "sat.euf": "false"}
   result = runner.args(params)
   assert "(set-option :smt.mbqi true)" in result
   assert "(set-option :sat.euf false)" in result


def test_args_tprefix_params_excluded(runner):
   # t__ params should not appear as set-option lines
   params = {"t__count": "0", "smt.mbqi": "true"}
   result = runner.args(params)
   assert "t__count" not in result
   assert "(set-option :smt.mbqi true)" in result


def test_args_no_tactics_when_no_t_count(runner):
   result = runner.args({"smt.mbqi": "true"})
   assert "check-sat-using" not in result
   assert "or-else" not in result


def test_args_no_tactics_when_count_zero(runner):
   params = {"t__count": "0"}
   result = runner.args(params)
   assert "check-sat-using" not in result


# --- args() — with tactics ---

def test_args_tactic_produces_commented_tactical(runner):
   params = _tactic_params(tactic_idx=0)  # simplify
   result = runner.args(params)
   assert ";(check-sat-using" in result


def test_args_tactic_contains_tactic_name(runner):
   params = _tactic_params(tactic_idx=0)  # simplify
   result = runner.args(params)
   assert "simplify" in result


def test_args_tactic_uses_or_else(runner):
   params = _tactic_params(tactic_idx=0)
   result = runner.args(params)
   assert "or-else" in result


def test_args_tactic_ends_with_smt(runner):
   params = _tactic_params(tactic_idx=0)
   result = runner.args(params)
   assert "(then " in result
   assert "smt)" in result


# --- tactical() helper ---

def test_tactical_none_without_count():
   assert tactical({}) is None


def test_tactical_none_with_zero_count():
   assert tactical({"t__count": "0"}) is None


def test_tactical_single_tactic():
   params = _tactic_params(tactic_idx=0)  # simplify, no bools/depths needed that aren't in params
   result = tactical(params)
   assert result is not None
   assert "simplify" in result
   assert result.startswith("(then ")
   assert result.endswith("smt)")


def test_tactical_uses_or_else_skip():
   # solve-eqs (index 1) has no BOOLS/DEPTHS — produces plain (or-else solve-eqs skip)
   params = _tactic_params(tactic_idx=1)
   result = tactical(params)
   assert "(or-else solve-eqs skip)" in result


def test_tactical_tactic_with_bool_options():
   # solve-eqs (index 1) has no BOOLS/DEPTHS entries — simple case
   params = _tactic_params(tactic_idx=1)  # solve-eqs
   result = tactical(params)
   assert "solve-eqs" in result
   assert "(or-else solve-eqs skip)" in result


def test_tactical_tactic_with_params():
   # ctx-simplify (index 8) has both BOOLS and DEPTHS
   params = _tactic_params(tactic_idx=8)
   result = tactical(params)
   assert "ctx-simplify" in result
   assert "using-params" in result


# --- success() ---

def test_success_unsat(runner):
   runner._solver.success = frozenset(["sat", "unsat"])
   assert runner.success("unsat")


def test_success_sat(runner):
   runner._solver.success = frozenset(["sat", "unsat"])
   assert runner.success("sat")


def test_success_unknown(runner):
   runner._solver.success = frozenset(["sat", "unsat"])
   assert not runner.success("unknown")


def test_success_timeout(runner):
   runner._solver.success = frozenset(["sat", "unsat"])
   assert not runner.success("timeout")


def test_success_error(runner):
   runner._solver.success = frozenset(["sat", "unsat"])
   assert not runner.success("error")


# --- run() with mocked solver ---

def _make_solver_mock(status="unsat", runtime=0.5, rlimit=12345, valid=True, solved=True):
   mock = MagicMock()
   mock.solve.return_value = {"status": status, "runtime": runtime, "rlimit-count": rlimit}
   mock.valid.return_value = valid
   mock.solved.return_value = solved
   mock.success = frozenset(["sat", "unsat"])
   return mock


def test_run_success(runner):
   runner._solver = _make_solver_mock(status="unsat", runtime=0.5, rlimit=12345)
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run({"smt.mbqi": "true"}, "problems/p1.smt2")
   quality, runtime, status, resources = result
   assert status == "unsat"
   assert runtime == pytest.approx(0.5)
   assert quality == 10 + int(1000 * 0.5)
   assert resources == 12345


def test_run_uses_rlimit_as_resource(runner):
   runner._solver = _make_solver_mock(rlimit=99999)
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run({}, "problems/p1.smt2")
   assert result[3] == 99999


def test_run_timeout_uses_penalty(runner):
   runner._solver = _make_solver_mock(status="timeout", valid=True, solved=False)
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run({}, "problems/p1.smt2")
   quality, runtime, status, resources = result
   assert quality == 100000000
   assert status == "timeout"


def test_run_invalid_result_returns_none(runner):
   runner._solver = _make_solver_mock(valid=False)
   runner._solver._output = "some error"
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run({}, "problems/p1.smt2")
   assert result is None


def test_run_exception_returns_none(runner):
   runner._solver.solve.side_effect = Exception("z3 crashed")
   runner._solver.valid.return_value = False
   runner._solver._output = ""
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run({}, "problems/p1.smt2")
   assert result is None


def test_run_calls_solve_with_correct_problem(runner):
   runner._solver = _make_solver_mock()
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      runner.run({"smt.mbqi": "true"}, "problems/p1.smt2")
   assert runner._solver.solve.call_args[0][0] == "/bench/problems/p1.smt2"


def test_run_strategy_contains_set_option(runner):
   runner._solver = _make_solver_mock()
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      runner.run({"smt.mbqi": "true"}, "problems/p1.smt2")
   strategy = runner._solver.solve.call_args[0][1]
   assert "(set-option :smt.mbqi true)" in strategy
