from typing import Any, Callable, TYPE_CHECKING
import logging

from ...builder.cvc5ml import Cvc5ML
from ...builder.enigma import Enigma
from .setup import Setup

if TYPE_CHECKING:
   from ...builder.builder import Builder

logger = logging.getLogger(__name__)

BuilderMaker = Callable[
   [Setup, Setup | None, dict[str, Any] | None],
   "Builder",
]


def autotuner(
      trains: Setup,
      devels: (Setup | None),
      tuneargs: (dict[str, Any] | None),
      mk_builder: BuilderMaker,
) -> Setup:
   if "refs" not in trains:
      assert "ref" in trains
      assert "sidlist" in trains
      ref = trains["ref"]
      idx = ref if (type(ref) is int) else 0
      trains["refs"] = [trains["sidlist"][idx]]
   trains["builder"] = mk_builder(trains, devels, tuneargs)
   return trains


def cvc5ml(
   trains: Setup,
   devels: (Setup | None) = None,
   tuneargs: (dict[str, Any] | None) = None,
) -> Setup:
   return autotuner(trains, devels, tuneargs, Cvc5ML)


def enigma(
   trains: Setup,
   devels: (Setup | None) = None,
   tuneargs: (dict[str, Any] | None) = None,
) -> Setup:
   return autotuner(trains, devels, tuneargs, Enigma)
