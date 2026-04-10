"""
Tests for VampireRunner.
No Vampire binary required — covers args(), clean(), success(), and run()
with a mocked solverpy solver.
"""

import pytest
from unittest.mock import MagicMock, patch

from grackle.runner.vampire import VampireRunner
from grackle.trainer.vampire.domain_full import DEFAULTS, REPLACE


# --- fixtures ---

def _mock_load_domain(self, cfg):
   self._domain = MagicMock()
   self._conds = {}


@pytest.fixture
def runner():
   with patch("grackle.runner.vampire.Vampire"), \
        patch("grackle.runner.runner.GrackleRunner.load_domain", _mock_load_domain):
      r = VampireRunner({"timeout": 10})
   return r


MINIMAL_PARAMS = {
   "avatar": "on",
   "selection": "10",
}


# --- args() ---

def test_args_returns_string(runner):
   assert isinstance(runner.args(MINIMAL_PARAMS), str)


def test_args_flag_format(runner):
   result = runner.args({"avatar": "on"})
   assert "--avatar on" in result


def test_args_sorted_alphabetically(runner):
   result = runner.args({"selection": "10", "avatar": "on"})
   assert result.index("--avatar") < result.index("--selection")


def test_args_double_underscore_and_replace(runner):
   # __ prefix stripped, then _ replaced by separator (age_weight_ratio: _ → :)
   result = runner.args({"age_weight_ratio": "__1_1"})
   assert "--age_weight_ratio 1:1" in result


def test_args_replace_separator_for_selection(runner):
   # selection: _ → -
   result = runner.args({"selection": "10"})
   assert "--selection 10" in result


def test_args_replace_separator_for_queue_ratios(runner):
   # avatar_split_queue_ratios: _ → ,
   result = runner.args({"avatar_split_queue_ratios": "__1_4"})
   assert "--avatar_split_queue_ratios 1,4" in result


def test_args_no_replace_for_plain_param(runner):
   result = runner.args({"binary_resolution": "on"})
   assert "--binary_resolution on" in result


def test_args_multiple_params(runner):
   params = {"avatar": "on", "binary_resolution": "off", "condensation": "fast"}
   result = runner.args(params)
   assert "--avatar on" in result
   assert "--binary_resolution off" in result
   assert "--condensation fast" in result


# --- clean() ---

def test_clean_removes_default_values(runner):
   # age_weight_ratio default is "__1_1"
   params = {"age_weight_ratio": "__1_1", "avatar": "off"}
   cleaned = runner.clean(params)
   assert "age_weight_ratio" not in cleaned


def test_clean_keeps_non_default_values(runner):
   params = {"age_weight_ratio": "__1_2", "avatar": "on"}
   cleaned = runner.clean(params)
   assert "age_weight_ratio" in cleaned
   assert cleaned["age_weight_ratio"] == "__1_2"


def test_clean_empty_when_all_defaults(runner):
   # pick two known defaults
   params = {k: DEFAULTS[k] for k in list(DEFAULTS)[:3]}
   cleaned = runner.clean(params)
   assert cleaned == {}


def test_clean_returns_dict(runner):
   assert isinstance(runner.clean({}), dict)


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

def _make_solver_mock(status="Theorem", runtime=1.2, active=500, valid=True, solved=True):
   mock = MagicMock()
   mock.solve.return_value = {"status": status, "runtime": runtime, "Active": active}
   mock.valid.return_value = valid
   mock.solved.return_value = solved
   mock.success = frozenset(["Theorem", "Unsatisfiable"])
   return mock


def test_run_success(runner):
   runner._solver = _make_solver_mock(status="Theorem", runtime=1.2, active=500)
   runner.config["penalty"] = 100000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run(MINIMAL_PARAMS, "TPTP/Problems/p1.p")
   quality, runtime, status, resources = result
   assert status == "Theorem"
   assert runtime == pytest.approx(1.2)
   assert quality == 10 + int(1000 * 1.2)
   assert resources == 500


def test_run_uses_active_as_resource(runner):
   runner._solver = _make_solver_mock(active=999)
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
   runner._solver._output = "some error"
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run(MINIMAL_PARAMS, "TPTP/Problems/p1.p")
   assert result is None


def test_run_exception_returns_none(runner):
   runner._solver.solve.side_effect = Exception("vampire crashed")
   runner._solver.valid.return_value = False
   runner._solver._output = ""
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run(MINIMAL_PARAMS, "TPTP/Problems/p1.p")
   assert result is None


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
      runner.run({"avatar": "on"}, "TPTP/Problems/p1.p")
   strategy = runner._solver.solve.call_args[0][1]
   assert "--avatar on" in strategy
