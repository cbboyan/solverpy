import logging

from ..solver.atp.eprover import E_STATIC, E
from ..solver.atp.prover9 import Prover9
from ..solver.atp.vampire import V_STATIC, Vampire
from ..solver.smt import Cvc5, Z3, Bitwuzla
from ..solver.smt.cvc5 import CVC5_STATIC
from .common import default, init, solver
from .setup import Setup

logger = logging.getLogger(__name__)


def eprover(setup: Setup) -> Setup:
   init(setup)
   default(setup, "static", E_STATIC.split())
   return solver(setup, E)


def vampire(setup: Setup) -> Setup:
   init(setup)
   default(setup, "static", V_STATIC.split())
   return solver(setup, Vampire)


def prover9(setup: Setup) -> Setup:
   init(setup)
   return solver(setup, Prover9)


def bitwuzla(setup: Setup) -> Setup:
   init(setup)
   return solver(setup, Bitwuzla)


def z3(setup: Setup) -> Setup:
   default(setup, "static", "")
   init(setup)
   return solver(setup, Z3)


def cvc5(setup: Setup) -> Setup:
   init(setup)
   default(setup, "static", CVC5_STATIC.split())
   return solver(setup, Cvc5)
