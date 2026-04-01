from pathlib import Path
import pytest

from solverpy.solver.atp.eprover import E
from solverpy.solver.atp.vampire import Vampire
from solverpy.solver.atp.lash import Lash
from solverpy.solver.atp.prover9 import Prover9
from solverpy.solver.smt.cvc5 import Cvc5
from solverpy.solver.smt.z3 import Z3
from solverpy.solver.smt.bitwuzla import Bitwuzla

DATA       = Path(__file__).parent / "data"
AGATHA_TPTP = DATA / "agatha.p"
AGATHA_SMT2 = DATA / "agatha.smt2"
AGATHA_LADR = DATA / "agatha.ladr"
THF_P       = DATA / "thf.p"
QF_BV_SMT2  = DATA / "qf_bv.smt2"
FINSET1     = DATA / "problems/bushy010/finset_1__t13_finset_1.p"

# Solvers under test — used by interface tests (no problem file needed).
SHELL_SOLVERS = [
   pytest.param(E("T5"),                      id="eprover"),
   pytest.param(E("T5", binary="eprover-ho"), id="eprover-ho"),
   pytest.param(Vampire("T5"),                id="vampire"),
   pytest.param(Lash("T5"),                   id="lash"),
   pytest.param(Cvc5("T5"),                   id="cvc5"),
   pytest.param(Bitwuzla("T5"),               id="bitwuzla"),
]

STDIN_SOLVERS = [
   pytest.param(Prover9("T5"),                id="prover9"),
   pytest.param(Z3("T5"),                     id="z3"),
]

SOLVERS = SHELL_SOLVERS + STDIN_SOLVERS

# (solver, problem, strategy, expected_status) — used by run tests.
CASES = [
   pytest.param((E("T5"),                      AGATHA_TPTP, "",                       "Theorem"), id="eprover-agatha"),
   pytest.param((E("T5", binary="eprover-ho"), THF_P,       "",                       "Theorem"), id="eprover-ho-thf"),
   pytest.param((Vampire("T5"),                AGATHA_TPTP, "",                       "Theorem"), id="vampire-agatha"),
   pytest.param((Vampire("T5"),                THF_P,       "",                       "Theorem"), id="vampire-thf"),
   pytest.param((Vampire("T5"),                FINSET1,     "",                       "Theorem"), id="vampire-bushy"),
   pytest.param((Lash("T5", static=f"-p tstp -M {DATA}"), THF_P, "-m empty", "Theorem"), id="lash-thf"),
   pytest.param((Prover9("T5"),                AGATHA_LADR, "",                       "Theorem"), id="prover9-agatha"),
   pytest.param((Cvc5("T5"),                   AGATHA_SMT2, "--full-saturate-quant",  "unsat"),   id="cvc5-agatha"),
   pytest.param((Z3("T5"),                     AGATHA_SMT2, "",                       "unsat"),   id="z3-agatha"),
   pytest.param((Bitwuzla("T5"),               QF_BV_SMT2,  "",                       "unsat"),   id="bitwuzla-qf-bv"),
]


@pytest.fixture(params=SOLVERS)
def solver(request):
   return request.param


@pytest.fixture(params=SHELL_SOLVERS)
def shell_solver(request):
   return request.param


@pytest.fixture(params=CASES)
def case(request):
   solver, problem, strategy, expected_status = request.param
   return (solver, str(problem), strategy, expected_status)
