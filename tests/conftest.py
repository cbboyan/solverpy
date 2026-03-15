import pytest

from solverpy.solver.atp.eprover import E

# Solvers under test.  Add more entries as binaries become available in CI.
SOLVERS = [
   pytest.param(E("T5"), id="eprover"),
   # pytest.param(Vampire("T5"), id="vampire"),
   # pytest.param(Cvc5("T5"),    id="cvc5"),
   # pytest.param(Z3("T5"),      id="z3"),
]


@pytest.fixture(params=SOLVERS)
def solver(request):
   return request.param
