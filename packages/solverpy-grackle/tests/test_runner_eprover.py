"""
Tests for EproverRunner.
No E binary required — covers args(), clean(), success(), and run()
with a mocked solverpy solver.
"""

import pytest
from unittest.mock import MagicMock, patch

from grackle.runner.eprover import EproverRunner, DEFAULTS, SINE_DEFAULTS


# --- fixtures ---

MINIMAL_PARAMS = {
   "sel": "SelectMaxLComplexAvoidPosPred",
   "tord": "LPO4",
   "tord_prec": "arity",
   "tord_weight": "arity",
   "simparamod": "none",
   "srd": "0",
   "forwardcntxtsr": "0",
   "splaggr": "0",
   "splcl": "0",
   "tord_const": "0",
   "sine": "0",
   "defcnf": "24",
   "prefer": "0",
   "fwdemod": "2",
   "der": "none",
   "presat": "0",
   "condense": "0",
   "slots": "1",
   "freq0": "1",
   "cef0": "ConjectureRelativeSymbolWeight__SimulateSOS__1_1_1_2__false__true__false__false__1_00__1_5__1_5__1__false__6",
}


def _mock_load_domain(self, cfg):
   self._domain = MagicMock()
   self._conds = {}


@pytest.fixture
def runner():
   with patch("grackle.runner.eprover.E"), \
        patch("grackle.runner.runner.GrackleRunner.load_domain", _mock_load_domain):
      r = EproverRunner({"timeout": 5})
   return r


# --- args() ---

def test_args_returns_string(runner):
   result = runner.args(MINIMAL_PARAMS)
   assert isinstance(result, str)


def test_args_contains_fixed_args(runner):
   result = runner.args(MINIMAL_PARAMS)
   assert "--delete-bad-limit=150000000" in result


def test_args_split_aggressive_on(runner):
   params = dict(MINIMAL_PARAMS, splaggr="1")
   assert "--split-aggressive" in runner.args(params)


def test_args_split_aggressive_off(runner):
   params = dict(MINIMAL_PARAMS, splaggr="0")
   assert "--split-aggressive" not in runner.args(params)


def test_args_srd_on(runner):
   params = dict(MINIMAL_PARAMS, srd="1")
   assert "--split-reuse-defs" in runner.args(params)


def test_args_forwardcntxtsr_on(runner):
   params = dict(MINIMAL_PARAMS, forwardcntxtsr="1")
   assert "--forward-context-sr" in runner.args(params)


def test_args_defcnf_value(runner):
   params = dict(MINIMAL_PARAMS, defcnf="24")
   assert "--definitional-cnf=24" in runner.args(params)


def test_args_defcnf_none_omitted(runner):
   params = dict(MINIMAL_PARAMS, defcnf="none")
   assert "--definitional-cnf" not in runner.args(params)


def test_args_der_std(runner):
   params = dict(MINIMAL_PARAMS, der="std")
   assert "--destructive-er" in runner.args(params)


def test_args_der_agg(runner):
   params = dict(MINIMAL_PARAMS, der="agg")
   result = runner.args(params)
   assert "--destructive-er" in result
   assert "--destructive-er-aggressive" in result


def test_args_simparamod_normal(runner):
   params = dict(MINIMAL_PARAMS, simparamod="normal")
   assert "--simul-paramod" in runner.args(params)


def test_args_simparamod_none_omitted(runner):
   params = dict(MINIMAL_PARAMS, simparamod="none")
   assert "--simul-paramod" not in runner.args(params)


def test_args_tord_lpo4(runner):
   params = dict(MINIMAL_PARAMS, tord="LPO4", tord_prec="arity")
   assert "-tLPO4" in runner.args(params)
   assert "-Garity" in runner.args(params)


def test_args_sine_omitted_when_zero(runner):
   params = dict(MINIMAL_PARAMS, sine="0")
   assert "GSinE" not in runner.args(params)


def test_args_sine_included_when_one(runner):
   params = dict(MINIMAL_PARAMS, sine="1", **SINE_DEFAULTS)
   assert "GSinE" in runner.args(params)


def test_args_heuristic_present(runner):
   result = runner.args(MINIMAL_PARAMS)
   assert "-H'" in result


# --- clean() ---

def test_clean_removes_excess_slots(runner):
   # slots=1 but freq1/cef1 present — should be removed
   params = dict(MINIMAL_PARAMS, slots="1", freq1="2", cef1="SomeHeuristic")
   cleaned = runner.clean(params)
   assert "freq1" not in cleaned
   assert "cef1" not in cleaned
   assert "freq0" in cleaned


def test_clean_keeps_used_slots(runner):
   params = dict(MINIMAL_PARAMS, slots="2",
                 freq1="2", cef1="SomeHeuristic")
   cleaned = runner.clean(params)
   assert "freq0" in cleaned
   assert "freq1" in cleaned


def test_clean_removes_sine_defaults_when_sine_off(runner):
   params = dict(MINIMAL_PARAMS, sine="0", **SINE_DEFAULTS)
   cleaned = runner.clean(params)
   for key in SINE_DEFAULTS:
      assert key not in cleaned


def test_clean_returns_none_without_slots(runner):
   params = {k: v for k, v in MINIMAL_PARAMS.items() if k != "slots"}
   assert runner.clean(params) is None


# --- success() ---

def test_success_theorem(runner):
   runner._solver.success = frozenset(["Theorem", "Unsatisfiable"])
   assert runner.success("Theorem")


def test_success_unsatisfiable(runner):
   runner._solver.success = frozenset(["Theorem", "Unsatisfiable"])
   assert runner.success("Unsatisfiable")


def test_success_timeout(runner):
   runner._solver.success = frozenset(["Theorem", "Unsatisfiable"])
   assert not runner.success("ResourceOut")


def test_success_error(runner):
   runner._solver.success = frozenset(["Theorem", "Unsatisfiable"])
   assert not runner.success("ERROR")


# --- run() with mocked solver ---

def _make_solver_mock(status="Theorem", runtime=1.5, processed=42, valid=True, solved=True):
   mock = MagicMock()
   mock.solve.return_value = {"status": status, "runtime": runtime, "Processed": processed}
   mock.valid.return_value = valid
   mock.solved.return_value = solved
   mock.success = frozenset(["Theorem", "Unsatisfiable"])
   return mock


def test_run_success(runner):
   runner._solver = _make_solver_mock(status="Theorem", runtime=1.5, processed=42)
   runner.config["penalty"] = 1000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run(MINIMAL_PARAMS, "problems/p1.p")
   quality, runtime, status, resources = result
   assert status == "Theorem"
   assert runtime == pytest.approx(1.5)
   assert quality == 10 + int(1000 * 1.5)
   assert resources == 42


def test_run_timeout_uses_penalty(runner):
   runner._solver = _make_solver_mock(status="ResourceOut", runtime=5.0, valid=True, solved=False)
   runner.config["penalty"] = 1000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run(MINIMAL_PARAMS, "problems/p1.p")
   quality, runtime, status, resources = result
   assert quality == 1000000
   assert status == "ResourceOut"


def test_run_invalid_result_returns_none(runner):
   runner._solver = _make_solver_mock(valid=False)
   runner._solver._output = "some error output"
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run(MINIMAL_PARAMS, "problems/p1.p")
   assert result is None


def test_run_exception_returns_none(runner):
   runner._solver.solve.side_effect = Exception("solver crashed")
   runner._solver.valid.return_value = False
   runner._solver._output = ""
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      result = runner.run(MINIMAL_PARAMS, "problems/p1.p")
   assert result is None


def test_run_calls_solve_with_correct_problem(runner):
   runner._solver = _make_solver_mock()
   runner.config["penalty"] = 1000000
   with patch.dict("os.environ", {"SOLVERPY_BENCHMARKS": "/bench"}):
      runner.run(MINIMAL_PARAMS, "problems/p1.p")
   call_args = runner._solver.solve.call_args
   assert call_args[0][0] == "/bench/problems/p1.p"
