import logging
import copy

from ..solver.atp.eprover import E_STATIC, E
from ..solver.atp.prover9 import Prover9
from ..solver.atp.vampire import V_STATIC, Vampire
from ..solver.smt import Cvc5, Z3, Bitwuzla, Llm2smt
from ..solver.smt.bitwuzla import BWZ_STATIC
from ..solver.smt.cvc5 import CVC5_STATIC
from ..solver.smt.llm2smt import LLM2SMT_STATIC
from ..solver.smt.z3 import Z3_STATIC
from ..solver.plugins.db.sid import Sid
from ..solver.plugins.db.eprovesid import EProverSid
from .common import default, init, make_solver
from .setup import Setup

logger = logging.getLogger(__name__)


def _evalset_solvers(setup: Setup, mk_solver, static: list[str] | None = None) -> Setup:
   assert "evals" in setup
   assert "plugins" in setup
   assert "options" in setup
   for key in ("evals", "devels"):
      if key not in setup:
         continue
      evalset = setup[key]
      default(evalset, "limit", "T1")
      default(evalset, "static", list(static or []))
      evalset["plugins"] = copy.deepcopy(setup["plugins"])
      evalset["solver"] = make_solver(
         evalset,
         mk_solver,
         evalset["plugins"],
         reloader=setup.get("reloader", False),
         options=setup["options"],
      )
   setup.pop("solver", None)
   return setup


def eprover(setup: Setup) -> Setup:
   assert "evals" in setup
   init(setup)
   assert "options" in setup
   assert "plugins" in setup
   plugins = [
      EProverSid() if isinstance(p, Sid) else p
      for p in setup["plugins"]
   ]
   setup["plugins"] = plugins
   for key in ("evals", "devels"):
      if key not in setup:
         continue
      evalset = setup[key]
      default(evalset, "limit", "T1")
      default(evalset, "static", E_STATIC.split())
      evalset["plugins"] = copy.deepcopy(plugins)
      evalset["solver"] = make_solver(
         evalset,
         E,
         evalset["plugins"],
         reloader=setup.get("reloader", False),
         options=setup["options"],
      )
   setup.pop("solver", None)
   return setup


def vampire(setup: Setup) -> Setup:
   init(setup)
   return _evalset_solvers(setup, Vampire, V_STATIC.split())


def prover9(setup: Setup) -> Setup:
   init(setup)
   return _evalset_solvers(setup, Prover9)


def bitwuzla(setup: Setup) -> Setup:
   init(setup)
   return _evalset_solvers(setup, Bitwuzla, BWZ_STATIC.split())


def z3(setup: Setup) -> Setup:
   init(setup)
   return _evalset_solvers(setup, Z3, Z3_STATIC.split())


def cvc5(setup: Setup) -> Setup:
   init(setup)
   return _evalset_solvers(setup, Cvc5, CVC5_STATIC.split())


def llm2smt(setup: Setup) -> Setup:
   init(setup)
   return _evalset_solvers(setup, Llm2smt, LLM2SMT_STATIC.split())
