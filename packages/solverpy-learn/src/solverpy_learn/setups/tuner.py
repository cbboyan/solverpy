from typing import Any, Callable, TYPE_CHECKING
import logging

from ..builder.cvc5ml import Cvc5ML
from ..builder.enigma import Enigma
from solverpy.setups.setup import Setup
from solverpy.setups.evalset import Evalset
from solverpy.setups.common import default

if TYPE_CHECKING:
   from ..builder.builder import Builder

logger = logging.getLogger(__name__)

BuilderMaker = Callable[..., "Builder"]


def defaultrefs(evalset: Evalset) -> None:
   if "refs" not in evalset:
      assert "ref" in evalset
      assert "strategies" in evalset
      ref = evalset["ref"]
      idx = ref if (type(ref) is int) else 0
      evalset["refs"] = [evalset["strategies"][idx]]


def defaultweight(setup: Setup, tune: dict[str, Any] | None) -> None:
   if not tune:
      return
   if ("posneg_weight" in setup) and ("posneg_weight" not in tune):
      tune["posneg_weight"] = setup["posneg_weight"]


def autotuner(
   mk_builder: BuilderMaker,
   setup: Setup,
   *args: Any,
   **kwargs: Any,
) -> Setup:
   assert "evals" in setup
   defaultrefs(setup["evals"])
   setup["builder"] = mk_builder(setup, *args, **kwargs)
   return setup


def cvc5ml(
   setup: Setup,
   tuneargs: (dict[str, Any] | None) = None,
) -> Setup:
   defaultweight(setup, tuneargs)
   return autotuner(Cvc5ML, setup, tuneargs)


def enigma(
   setup: Setup,
   tunesel: (dict[str, Any] | None) = None,
   tunegen: (dict[str, Any] | None) = None,
) -> Setup:
   default(setup, "templates", None)
   defaultweight(setup, tunesel)
   defaultweight(setup, tunegen)
   assert "templates" in setup
   return autotuner(
      Enigma,
      setup,
      tunesel,
      tunegen,
      templates=setup["templates"],
   )
