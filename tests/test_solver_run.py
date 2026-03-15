"""
Tests that actually launch the solver binary.
Requires the solver binary to be installed and in PATH.
Tests are skipped automatically if the binary is not found.
"""

import pytest
from pathlib import Path

from solverpy.solver.atp.eprover import E
from solverpy.solver.atp.vampire import Vampire
from solverpy.solver.atp.lash import Lash
from solverpy.solver.atp.prover9 import Prover9
from solverpy.solver.smt.cvc5 import Cvc5
from solverpy.solver.smt.z3 import Z3
from solverpy.solver.smt.bitwuzla import Bitwuzla

DATA_DIR = Path(__file__).parent / "data"
AGATHA_TPTP = DATA_DIR / "agatha.p"
AGATHA_SMT2 = DATA_DIR / "agatha.smt2"
AGATHA_LADR = DATA_DIR / "agatha.ladr"
THF_P       = DATA_DIR / "thf.p"
QF_BV_SMT2  = DATA_DIR / "qf_bv.smt2"
STRATEGY = ""  # default strategy: no extra options

CVC5_STRATEGY = "--full-saturate-quant"
LASH_STRATEGY = f"-m empty -M {DATA_DIR}"

ATP_SOLVERS = (E, Vampire, Lash, Prover9)

FORMAT_INCOMPATIBLE = ()


@pytest.fixture(autouse=True)
def require_binary(solver):
   if not solver.isinstalled():
      pytest.skip(f"solver binary not found: {solver._binary}")


_cache: dict = {}


@pytest.fixture
def agatha(solver):
   if isinstance(solver, Lash):
      return str(THF_P)
   if isinstance(solver, Prover9):
      return str(AGATHA_LADR)
   if isinstance(solver, ATP_SOLVERS):
      return str(AGATHA_TPTP)
   if isinstance(solver, Bitwuzla):
      return str(QF_BV_SMT2)
   return str(AGATHA_SMT2)


@pytest.fixture
def strategy(solver):
   if isinstance(solver, Cvc5):
      return CVC5_STRATEGY
   if isinstance(solver, Lash):
      return LASH_STRATEGY
   return STRATEGY


@pytest.fixture
def agatha_compatible(solver):
   """False if the solver cannot parse the agatha test problem format."""
   return not isinstance(solver, FORMAT_INCOMPATIBLE)


@pytest.fixture
def agatha_expected_status(solver):
   """Expected status when agatha is solved; None if solver won't solve it."""
   if isinstance(solver, (Cvc5, Z3, Bitwuzla)):
      return "unsat"
   return "Theorem"  # E, Vampire, Lash, Prover9



@pytest.fixture
def agatha_output(solver, agatha, strategy):
   key = f"{solver}:run"
   if key not in _cache:
      _cache[key] = solver.run(agatha, strategy)
   return _cache[key]


@pytest.fixture
def agatha_result(solver, agatha, strategy):
   key = f"{solver}:solve"
   if key not in _cache:
      _cache[key] = solver.solve(agatha, strategy)
   return _cache[key]


# --- run() ---

def test_run_returns_string(agatha_output):
   assert isinstance(agatha_output, str)


def test_run_nonempty(agatha_output):
   assert len(agatha_output) > 0


def test_run_contains_instance(agatha, agatha_output):
   name = Path(agatha).stem  # "agatha", "thf", etc.
   assert name in agatha_output.lower()


# --- solve() ---

def test_solve_returns_dict(agatha_result):
   assert isinstance(agatha_result, dict)


def test_solve_has_status(solver, agatha_result, agatha_compatible):
   if not agatha_compatible:
      pytest.skip(f"{solver._binary} cannot parse agatha problem format")
   assert "status" in agatha_result


def test_solve_has_runtime(agatha_result):
   assert "runtime" in agatha_result
   assert isinstance(agatha_result["runtime"], float)
   assert agatha_result["runtime"] >= 0.0


def test_solve_valid_result(solver, agatha_result, agatha_compatible):
   if not agatha_compatible:
      pytest.skip(f"{solver._binary} cannot parse agatha problem format")
   assert solver.valid(agatha_result)


def test_solve_status_in_statuses(solver, agatha_result, agatha_compatible):
   if not agatha_compatible:
      pytest.skip(f"{solver._binary} cannot parse agatha problem format")
   assert agatha_result["status"] in solver.statuses


def test_solve_agatha_solved(solver, agatha_result, agatha_expected_status):
   if agatha_expected_status is None:
      pytest.skip(f"{solver._binary} not expected to solve agatha")
   assert solver.solved(agatha_result)


def test_solve_agatha_status(solver, agatha_result, agatha_expected_status):
   if agatha_expected_status is None:
      pytest.skip(f"{solver._binary} not expected to solve agatha")
   assert agatha_result["status"] == agatha_expected_status


def test_solve_runtime_within_limit(solver, agatha_result):
   assert agatha_result["runtime"] <= solver._limits.timeout + 1  # +1 for system overhead
