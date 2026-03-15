import pytest

from solverpy.solver.atp.eprover import E
from solverpy.solver.atp.vampire import Vampire
from solverpy.solver.atp.lash import Lash
from solverpy.solver.atp.prover9 import Prover9
from solverpy.solver.smt.cvc5 import Cvc5
from solverpy.solver.smt.z3 import Z3
from solverpy.solver.smt.bitwuzla import Bitwuzla

SOLVERS = [
   pytest.param(E("T5"),        id="eprover"),
   pytest.param(Vampire("T5"),  id="vampire"),
   pytest.param(Lash("T5"),     id="lash"),
   pytest.param(Prover9("T5"),  id="prover9"),
   pytest.param(Cvc5("T5"),     id="cvc5"),
   pytest.param(Z3("T5"),       id="z3"),
   pytest.param(Bitwuzla("T5"), id="bitwuzla"),
]


@pytest.fixture(params=SOLVERS)
def solver(request):
   return request.param
