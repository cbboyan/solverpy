"""
Tests for Cvc5Runner.
No CVC5 binary required — covers args(), clean(), success(), and run()
with a mocked solverpy solver.
"""

import pytest
from unittest.mock import MagicMock, patch

from grackle.runner.cvc5 import Cvc5Runner
from grackle.trainer.cvc5.domain import DEFAULTS


# --- fixtures ---

def _mock_load_domain(self, cfg):
   self._domain = MagicMock()
   self._conds = {}


@pytest.fixture
def runner():
   with patch("grackle.runner.cvc5.Cvc5"), \
        patch("grackle.runner.runner.GrackleRunner.load_domain", _mock_load_domain):
      r = Cvc5Runner({"timeout": 10})
   return r


@pytest.fixture
def runner_rlimit():
   with patch("grackle.runner.cvc5.Cvc5") as mock_cvc5, \
        patch("grackle.runner.runner.GrackleRunner.load_domain", _mock_load_domain):
      r = Cvc5Runner({"timeout": 10, "rlimit": 500000})
   return r, mock_cvc5


# --- args() ---

def test_args_yes_becomes_flag(runner):
   assert "--cbqi" in runner.args({"cbqi": "yes"})


def test_args_no_becomes_no_flag(runner):
   assert "--no-cbqi" in runner.args({"cbqi": "no"})


def test_args_value_param(runner):
   assert "--simplification=batch" in runner.args({"simplification": "batch"})


def test_args_underscore_to_dash_in_name(runner):
   assert "--finite-model-find" in runner.args({"finite_model_find": "yes"})


def test_args_underscore_to_dash_in_value(runner):
   assert "--quant-dsplit=no-split" in runner.args({"quant_dsplit": "no_split"})


def test_args_sorted_alphabetically(runner):
   result = runner.args({"simplification": "none", "cbqi": "yes"})
   assert result.index("--cbqi") < result.index("--simplification")


def test_args_multiple_params(runner):
   params = {"cbqi": "yes", "simplification": "batch", "static_learning": "no"}
   result = runner.args(params)
   assert "--cbqi" in result
   assert "--simplification=batch" in result
   assert "--no-static-learning" in result


# --- clean() ---

def test_clean_removes_default_values(runner):
   # cbqi default is 'yes'
   params = {"cbqi": "yes", "simplification": "none"}
   cleaned = runner.clean(params)
   assert "cbqi" not in cleaned


def test_clean_keeps_non_default_values(runner):
   params = {"cbqi": "no", "simplification": "batch"}
   cleaned = runner.clean(params)
   assert "cbqi" in cleaned
   assert cleaned["cbqi"] == "no"


def test_clean_removes_conditioned_param_when_parent_unset(runner):
   # cbqi_all_conflict | cbqi in {yes}
   # if cbqi=no (not in {yes}), cbqi_all_conflict should be removed
   params = {"cbqi": "no", "cbqi_all_conflict": "yes"}
   cleaned = runner.clean(params)
   assert "cbqi_all_conflict" not in cleaned


def test_clean_keeps_conditioned_param_when_parent_set(runner):
   # cbqi_all_conflict active when cbqi=yes
   params = {"cbqi": "yes", "cbqi_all_conflict": "yes"}
   cleaned = runner.clean(params)
   assert "cbqi_all_conflict" in cleaned


def test_clean_empty_when_all_defaults(runner):
   params = {k: DEFAULTS[k] for k in list(DEFAULTS)[:5]}
   assert runner.clean(params) == {}


def test_clean_returns_dict(runner):
   assert isinstance(runner.clean({}), dict)


# --- limit string with rlimit ---

def test_rlimit_included_in_limit_string(runner_rlimit):
   runner, mock_cvc5 = runner_rlimit
   call_kwargs = mock_cvc5.call_args
   limit_arg = call_kwargs[1].get("limit") or call_kwargs[0][0]
   assert "R500000" in limit_arg


def test_no_rlimit_uses_time_only(runner):
   # runner fixture has no rlimit — limit should be T10 only
   with patch("grackle.runner.cvc5.Cvc5") as mock_cvc5, \
        patch("grackle.runner.runner.GrackleRunner.load_domain", _mock_load_domain):
      Cvc5Runner({"timeout": 10})
   limit_arg = mock_cvc5.call_args[1].get("limit") or mock_cvc5.call_args[0][0]
   assert limit_arg == "T10"
   assert "R" not in limit_arg


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


# --- run() with mocked solver ---

def _make_solver_mock(status="unsat", runtime=0.8, resources=42000, valid=True, solved=True):
   mock = MagicMock()
   mock.solve.return_value = {
      "status": status,
      "runtime": runtime,
      "resource::resourceUnitsUsed": resources,
   }
   mock.valid.return_value = valid
   mock.solved.return_value = solved
   mock.success = frozenset(["sat", "unsat"])
   return mock


def test_run_success(runner):
   runner._solver = _make_solver_mock(status="unsat", runtime=0.8, resources=42000)
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run({"cbqi": "no"}, "problems/p1.smt2")
   quality, runtime, status, res = result
   assert status == "unsat"
   assert runtime == pytest.approx(0.8)
   assert quality == 10 + int(1000 * 0.8)
   assert res == 42000


def test_run_uses_resource_units(runner):
   runner._solver = _make_solver_mock(resources=99999)
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run({}, "problems/p1.smt2")
   assert result[3] == 99999


def test_run_timeout_uses_penalty(runner):
   runner._solver = _make_solver_mock(status="timeout", valid=True, solved=False)
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run({}, "problems/p1.smt2")
   assert result[0] == 100000000
   assert result[2] == "timeout"


def test_run_invalid_result_returns_none(runner):
   runner._solver = _make_solver_mock(valid=False)
   runner._solver._output = "error"
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      assert runner.run({}, "problems/p1.smt2") is None


def test_run_exception_returns_none(runner):
   runner._solver.solve.side_effect = Exception("cvc5 crashed")
   runner._solver.valid.return_value = False
   runner._solver._output = ""
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      assert runner.run({}, "problems/p1.smt2") is None


def test_run_calls_solve_with_correct_problem(runner):
   runner._solver = _make_solver_mock()
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      runner.run({"cbqi": "no"}, "problems/p1.smt2")
   assert runner._solver.solve.call_args[0][0] == "/bench/problems/p1.smt2"
