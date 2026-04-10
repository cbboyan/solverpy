"""
Integration tests — actually invoke the solver binaries.
Requires SOLVERPY_BENCHMARKS to point at a directory with problem files.
Each test is skipped automatically if the relevant binary is not in PATH.

Run as: SOLVERPY_BENCHMARKS=/path/to/solverpy/tests/data pytest tests/integration/
"""

import os
import shutil
import pytest
from unittest.mock import patch

from .conftest import mock_domain, z3_domain

BENCHMARKS = os.getenv("SOLVERPY_BENCHMARKS", ".")

TPTP_PROBLEM = "agatha.p"
THF_PROBLEM  = "thf.p"
SMT_PROBLEM  = "agatha.smt2"

# Simple E heuristic that parses cleanly with E 3.x
EPROVER_PARAMS = {
   "sel": "SelectMaxLComplexAvoidPosPred",
   "tord": "LPO4", "tord_prec": "arity", "tord_weight": "arity",
   "simparamod": "none", "srd": "0", "forwardcntxtsr": "0",
   "splaggr": "0", "splcl": "0", "tord_const": "0", "sine": "0",
   "defcnf": "24", "prefer": "0", "fwdemod": "2", "der": "none",
   "presat": "0", "condense": "0",
   "slots": "1", "freq0": "1",
   "cef0": "Clauseweight__ConstPrio__1__1__1",
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _check_result(result):
   assert result is not None, "runner.run() returned None"
   assert len(result) == 4
   quality, runtime, status, resources = result
   assert isinstance(quality, int)
   assert isinstance(runtime, float) and runtime >= 0.0
   assert isinstance(status, str) and len(status) > 0
   assert isinstance(resources, (int, float))


# ---------------------------------------------------------------------------
# E Prover
# ---------------------------------------------------------------------------

@pytest.fixture
def eprover_runner():
   if not shutil.which("eprover"):
      pytest.skip("eprover not installed")
   from grackle.runner.eprover import EproverRunner
   with patch("grackle.runner.runner.GrackleRunner.load_domain", mock_domain):
      return EproverRunner({"timeout": 10})

def test_eprover_run_returns_result(eprover_runner):
   _check_result(eprover_runner.run(EPROVER_PARAMS, TPTP_PROBLEM))

def test_eprover_run_solves(eprover_runner):
   result = eprover_runner.run(EPROVER_PARAMS, TPTP_PROBLEM)
   assert result is not None and eprover_runner.success(result[2])

def test_eprover_resource_is_processed_count(eprover_runner):
   result = eprover_runner.run(EPROVER_PARAMS, TPTP_PROBLEM)
   assert result is not None and result[3] > 0


# ---------------------------------------------------------------------------
# Vampire
# ---------------------------------------------------------------------------

@pytest.fixture
def vampire_runner():
   if not shutil.which("vampire"):
      pytest.skip("vampire not installed")
   from grackle.runner.vampire import VampireRunner
   with patch("grackle.runner.runner.GrackleRunner.load_domain", mock_domain):
      return VampireRunner({"timeout": 10})

def test_vampire_run_returns_result(vampire_runner):
   _check_result(vampire_runner.run({}, TPTP_PROBLEM))

def test_vampire_run_solves(vampire_runner):
   result = vampire_runner.run({}, TPTP_PROBLEM)
   assert result is not None and vampire_runner.success(result[2])

def test_vampire_resource_is_active_clauses(vampire_runner):
   result = vampire_runner.run({}, TPTP_PROBLEM)
   assert result is not None and result[3] >= 0


# ---------------------------------------------------------------------------
# Lash  (needs -m empty and the mode dir passed via static)
# ---------------------------------------------------------------------------

@pytest.fixture
def lash_runner():
   if not shutil.which("lash"):
      pytest.skip("lash not installed")
   from grackle.runner.lash import LashRunner
   with patch("grackle.runner.runner.GrackleRunner.load_domain", mock_domain):
      return LashRunner({"timeout": 10, "lstatic": f"-p tstp -m empty -M {BENCHMARKS}"})

def test_lash_run_returns_result(lash_runner):
   _check_result(lash_runner.run({}, THF_PROBLEM))

def test_lash_run_solves(lash_runner):
   result = lash_runner.run({}, THF_PROBLEM)
   assert result is not None and lash_runner.success(result[2])

def test_lash_resource_is_steps(lash_runner):
   result = lash_runner.run({}, THF_PROBLEM)
   assert result is not None and isinstance(result[3], (int, float))


# ---------------------------------------------------------------------------
# Z3
# ---------------------------------------------------------------------------

@pytest.fixture
def z3_runner():
   if not shutil.which("z3"):
      pytest.skip("z3 not installed")
   from grackle.runner.z3 import Z3Runner
   with patch("grackle.runner.runner.GrackleRunner.load_domain", z3_domain):
      return Z3Runner({"timeout": 10})

def test_z3_run_returns_result(z3_runner):
   _check_result(z3_runner.run({}, SMT_PROBLEM))

def test_z3_run_solves(z3_runner):
   result = z3_runner.run({}, SMT_PROBLEM)
   assert result is not None and z3_runner.success(result[2])

def test_z3_resource_is_rlimit(z3_runner):
   result = z3_runner.run({}, SMT_PROBLEM)
   assert result is not None and result[3] >= 0


# ---------------------------------------------------------------------------
# CVC5  (needs --full-saturate-quant to handle quantifiers in agatha.smt2)
# ---------------------------------------------------------------------------

@pytest.fixture
def cvc5_runner():
   if not shutil.which("cvc5"):
      pytest.skip("cvc5 not installed")
   from grackle.runner.cvc5 import Cvc5Runner
   with patch("grackle.runner.runner.GrackleRunner.load_domain", mock_domain):
      return Cvc5Runner({"timeout": 10})

def test_cvc5_run_returns_result(cvc5_runner):
   _check_result(cvc5_runner.run({"full_saturate_quant": "yes"}, SMT_PROBLEM))

def test_cvc5_run_solves(cvc5_runner):
   result = cvc5_runner.run({"full_saturate_quant": "yes"}, SMT_PROBLEM)
   assert result is not None and cvc5_runner.success(result[2])

def test_cvc5_resource_is_resource_units(cvc5_runner):
   result = cvc5_runner.run({"full_saturate_quant": "yes"}, SMT_PROBLEM)
   assert result is not None and result[3] >= 0
