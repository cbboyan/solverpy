"""
Tests for LashRunner.
No Lash binary required — covers args(), clean(), success(), and run()
with a mocked solverpy solver.
"""

import pytest
from unittest.mock import MagicMock, patch

from grackle.runner.lash import LashRunner
from grackle.trainer.lash.domain import DEFAULTS


# --- fixtures ---

def _mock_load_domain(self, cfg):
   self._domain = MagicMock()
   self._conds = {}


@pytest.fixture
def runner():
   with patch("grackle.runner.lash.Lash"), \
        patch("grackle.runner.runner.GrackleRunner.load_domain", _mock_load_domain):
      r = LashRunner({"timeout": 10})
   return r


MINIMAL_PARAMS = {
   "AP_WEIGHT": "2",
   "CHOICE": "true",
}


# --- args() ---

def test_args_returns_string(runner):
   assert isinstance(runner.args(MINIMAL_PARAMS), str)


def test_args_flag_format(runner):
   result = runner.args({"AP_WEIGHT": "2"})
   assert "-flag AP_WEIGHT 2" in result


def test_args_sorted_alphabetically(runner):
   result = runner.args({"CHOICE": "true", "AP_WEIGHT": "2"})
   assert result.index("AP_WEIGHT") < result.index("CHOICE")


def test_args_multiple_params(runner):
   result = runner.args({"AP_WEIGHT": "2", "CHOICE": "true", "AXIOM_DELAY": "1"})
   assert "-flag AP_WEIGHT 2" in result
   assert "-flag CHOICE true" in result
   assert "-flag AXIOM_DELAY 1" in result


def test_args_empty_params(runner):
   assert runner.args({}) == ""


# --- clean() ---

def test_clean_removes_default_values(runner):
   # ALL_DEFS_AS_EQNS default is "false"
   params = {"ALL_DEFS_AS_EQNS": "false", "AP_WEIGHT": "2"}
   cleaned = runner.clean(params)
   assert "ALL_DEFS_AS_EQNS" not in cleaned


def test_clean_keeps_non_default_values(runner):
   params = {"ALL_DEFS_AS_EQNS": "true", "AP_WEIGHT": "1"}
   cleaned = runner.clean(params)
   assert "ALL_DEFS_AS_EQNS" in cleaned
   assert "AP_WEIGHT" not in cleaned  # AP_WEIGHT default is "1"


def test_clean_empty_when_all_defaults(runner):
   params = {k: DEFAULTS[k] for k in list(DEFAULTS)[:5]}
   assert runner.clean(params) == {}


def test_clean_returns_dict(runner):
   assert isinstance(runner.clean({}), dict)


# --- static string uses LASH_MODE_DIR ---

def test_static_uses_lash_mode_dir():
   with patch("grackle.runner.lash.Lash") as mock_lash, \
        patch("grackle.runner.runner.GrackleRunner.load_domain", _mock_load_domain), \
        patch.dict("os.environ", {"LASH_MODE_DIR": "/my/modes"}):
      LashRunner({"timeout": 5})
   static_arg = mock_lash.call_args[1].get("static") or mock_lash.call_args[0][2]
   assert "/my/modes" in static_arg


def test_static_config_override():
   with patch("grackle.runner.lash.Lash") as mock_lash, \
        patch("grackle.runner.runner.GrackleRunner.load_domain", _mock_load_domain):
      LashRunner({"timeout": 5, "lstatic": "-p tstp -m mymode"})
   static_arg = mock_lash.call_args[1].get("static") or mock_lash.call_args[0][2]
   assert static_arg == "-p tstp -m mymode"


# --- success() ---

def test_success_theorem(runner):
   runner._solver.success = frozenset(["Theorem", "Unsatisfiable", "Satisfiable",
                                        "CounterSatisfiable", "ContradictoryAxioms"])
   assert runner.success("Theorem")


def test_success_unsatisfiable(runner):
   runner._solver.success = frozenset(["Theorem", "Unsatisfiable"])
   assert runner.success("Unsatisfiable")


def test_success_resource_out(runner):
   runner._solver.success = frozenset(["Theorem", "Unsatisfiable"])
   assert not runner.success("ResourceOut")


def test_success_gave_up(runner):
   runner._solver.success = frozenset(["Theorem", "Unsatisfiable"])
   assert not runner.success("GaveUp")


# --- run() with mocked solver ---

def _make_solver_mock(status="Theorem", runtime=1.0, steps=100, valid=True, solved=True):
   mock = MagicMock()
   mock.solve.return_value = {"status": status, "runtime": runtime, "Steps": steps}
   mock.valid.return_value = valid
   mock.solved.return_value = solved
   mock.success = frozenset(["Theorem", "Unsatisfiable"])
   return mock


def test_run_success(runner):
   runner._solver = _make_solver_mock(status="Theorem", runtime=1.0, steps=100)
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run(MINIMAL_PARAMS, "TPTP/Problems/p1.p")
   quality, runtime, status, resources = result
   assert status == "Theorem"
   assert runtime == pytest.approx(1.0)
   assert quality == 10 + int(1000 * 1.0)
   assert resources == 100


def test_run_uses_steps_as_resource(runner):
   runner._solver = _make_solver_mock(steps=999)
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run(MINIMAL_PARAMS, "TPTP/Problems/p1.p")
   assert result[3] == 999


def test_run_timeout_uses_penalty(runner):
   runner._solver = _make_solver_mock(status="ResourceOut", valid=True, solved=False)
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run(MINIMAL_PARAMS, "TPTP/Problems/p1.p")
   assert result[0] == 100000000
   assert result[2] == "ResourceOut"


def test_run_invalid_result_returns_none(runner):
   runner._solver = _make_solver_mock(valid=False)
   runner._solver._output = "error"
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      assert runner.run(MINIMAL_PARAMS, "TPTP/Problems/p1.p") is None


def test_run_exception_returns_none(runner):
   runner._solver.solve.side_effect = Exception("lash crashed")
   runner._solver.valid.return_value = False
   runner._solver._output = ""
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      assert runner.run(MINIMAL_PARAMS, "TPTP/Problems/p1.p") is None


def test_run_calls_solve_with_correct_problem(runner):
   runner._solver = _make_solver_mock()
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      runner.run(MINIMAL_PARAMS, "TPTP/Problems/p1.p")
   assert runner._solver.solve.call_args[0][0] == "/bench/TPTP/Problems/p1.p"


def test_run_strategy_contains_flag(runner):
   runner._solver = _make_solver_mock()
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      runner.run({"AP_WEIGHT": "2"}, "TPTP/Problems/p1.p")
   strategy = runner._solver.solve.call_args[0][1]
   assert "-flag AP_WEIGHT 2" in strategy
