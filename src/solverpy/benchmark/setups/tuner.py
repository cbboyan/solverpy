from typing import Any, Callable, TYPE_CHECKING
import logging

from ...builder.cvc5ml import Cvc5ML
from ...builder.enigma import Enigma
from .setup import Setup

if TYPE_CHECKING:
   from ...builder.builder import Builder

logger = logging.getLogger(__name__)

BuilderMaker = Callable[..., "Builder"]

def defaultrefs(trains: Setup) -> None:
   if "refs" not in trains:
      assert "ref" in trains
      assert "sidlist" in trains
      ref = trains["ref"]
      idx = ref if (type(ref) is int) else 0
      trains["refs"] = [trains["sidlist"][idx]]

def autotuner(
      mk_builder: BuilderMaker,
      trains: Setup,
      *args: Any,
      **kwargs: Any,
) -> Setup:
   defaultrefs(trains)
   trains["builder"] = mk_builder(trains, *args, **kwargs)
   return trains


def cvc5ml(
   trains: Setup,
   devels: (Setup | None) = None,
   tuneargs: (dict[str, Any] | None) = None,
) -> Setup:
   return autotuner(Cvc5ML, trains, devels, tuneargs)


def enigma(
   trains: Setup,
   devels: (Setup | None) = None,
   tunesel: (dict[str, Any] | None) = None,
   tunegen: (dict[str, Any] | None) = None,
) -> Setup:
   return autotuner(Enigma, trains, devels, tunesel, tunegen)
