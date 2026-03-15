import logging

from solverpy.solver.atp.eprover import E_STATIC
from solverpy.setups.common import default
from solverpy.setups.setup import Setup
from ..builder.plugins import (
   EnigmaTrains,
   EnigmaMultiTrains,
   EnigmaTrainsDebug,
   Cvc5Trains,
   Cvc5TrainsDebug,
)

logger = logging.getLogger(__name__)


def eprover(setup: Setup, training: bool = False) -> Setup:
   from solverpy.setups.solver import eprover as _eprover_base
   _eprover_base(setup)
   if not training:
      return setup
   assert "plugins" in setup
   assert "options" in setup
   static = setup["static"]
   default(setup, "dataname", "data/model")
   assert "dataname" in setup
   default(setup, "e_training_examples", "11")
   assert "e_training_examples" in setup
   default(setup, "sel_features", None)
   assert "sel_features" in setup
   default(setup, "gen_features", None)
   assert "gen_features" in setup
   default(setup, "posneg_ratio", 0)
   assert "posneg_ratio" in setup
   sel = setup["sel_features"]
   gen = setup["gen_features"]
   dataname = setup["dataname"]
   ratio = setup["posneg_ratio"]
   static.append(f"--training-examples={setup['e_training_examples']}")
   if sel:
      static.append(f'--enigmatic-sel-features="{sel}"')
   if gen:
      static.append(f'--enigmatic-gen-features="{gen}"')
   if sel and gen:
      trains = EnigmaMultiTrains(dataname, sel, gen, ratio)
   elif sel:
      trains = EnigmaTrains(dataname, sel, "sel", ratio)
   elif gen:
      trains = EnigmaTrains(dataname, gen, "gen", ratio)
   else:
      raise ValueError(
         "`sel_features` or `gen_features` must be provided in setup to generate trains."
      )
   setup["trains"] = trains
   plugs = setup["plugins"]
   plugs.append(trains)
   flatten = "flatten" in setup["options"]
   if "debug-trains" in setup["options"]:
      if sel:
         plugs.append(EnigmaTrainsDebug(sel, "sel", flatten, ratio))
      if gen:
         plugs.append(EnigmaTrainsDebug(gen, "gen", flatten, ratio))
   return setup


def cvc5(setup: Setup, training: bool = False) -> Setup:
   from solverpy.setups.solver import cvc5 as _cvc5_base
   _cvc5_base(setup)
   if not training:
      return setup
   assert "plugins" in setup
   assert "options" in setup
   static = setup["static"]
   static.extend([
      "--produce-proofs",
      "--produce-models",
      "--dump-instantiations",
      "--print-inst-full",
      "--ml-engine",
   ])
   default(setup, "dataname", "data/model")
   assert "dataname" in setup
   default(setup, "posneg_ratio", 0)
   assert "posneg_ratio" in setup
   ratio = setup["posneg_ratio"]
   trains = Cvc5Trains(setup["dataname"], ratio)
   plugs = setup["plugins"]
   plugs.append(trains)
   options = setup["options"]
   if "debug-trains" in options:
      plugs.append(Cvc5TrainsDebug("flatten" in options, ratio))
   setup["trains"] = trains
   return setup
