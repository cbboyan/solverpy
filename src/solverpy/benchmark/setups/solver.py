import logging

from ...solver.atp.eprover import E_STATIC, E
from ...solver.atp.prover9 import Prover9
from ...solver.atp.vampire import Vampire
from ...builder.plugins import *
from ...solver.smt import Cvc5
from ...solver.smt import Bitwuzla
from ...solver.smt.cvc5 import CVC5_STATIC
from .common import default, init, solver
from .setup import Setup

logger = logging.getLogger(__name__)


def eprover(setup: Setup, training: bool = False) -> Setup:
   init(setup)
   assert "plugins" in setup
   assert "options" in setup
   if training:
      default(setup, "dataname", "data/model")
      assert "dataname" in setup
      default(setup, "e_training_examples", "11")
      assert "e_training_examples" in setup
      default(setup, "static", E_STATIC)
      assert "static" in setup
      default(setup, "sel_features", None)
      assert "sel_features" in setup
      default(setup, "gen_features", None)
      assert "gen_features" in setup
      sel = setup["sel_features"]
      gen = setup["gen_features"]
      dataname = setup["dataname"]
      setup["static"] += f" --training-examples={setup['e_training_examples']}"
      if sel:
         setup["static"] += f' --enigmatic-sel-features="{sel}"'
      if gen:
         setup["static"] += f' --enigmatic-gen-features="{gen}"'
      if sel and gen:
         trains = EnigmaMultiTrains(dataname, sel, gen)
      elif sel:
         trains = EnigmaTrains(dataname, sel, "sel")
      elif gen:
         trains = EnigmaTrains(dataname, gen, "gen")
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
            plugs.append(EnigmaTrainsDebug(sel, "sel", flatten))
         if gen:
            plugs.append(EnigmaTrainsDebug(gen, "gen", flatten))

      ####default(setup, "sel_features", "C(l,v,h,s,c,d,a)")
      ###setup["static"] += " ".join(["", # make a space
      ###   f"--training-examples={setup['e_training_examples']}",
      ###   f"--enigmatic-sel-features=\"{setup['sel_features']}\"",
      ###])
      ###default(setup, "dataname", "data/model")
      ###trains = EnigmaTrains(setup["dataname"], setup["sel_features"])
      ###plugs = setup["plugins"]
      ###plugs.append(trains)
      ###if "debug-trains" in setup["options"]:
      ###   plugs.append(EnigmaTrainsDebug(
      ###      setup["sel_features"], "flatten" in setup["options"]))
      ###setup["trains"] = trains
   return solver(setup, E)


def vampire(setup: Setup) -> Setup:
   init(setup)
   return solver(setup, Vampire)


def prover9(setup: Setup) -> Setup:
   init(setup)
   return solver(setup, Prover9)


def bitwuzla(setup: Setup) -> Setup:
   init(setup)
   return solver(setup, Bitwuzla)


def cvc5(setup: Setup, training: bool = False) -> Setup:
   init(setup)
   assert "plugins" in setup
   assert "options" in setup
   if training:
      static = CVC5_STATIC + " ".join([
         "--produce-proofs",
         "--produce-models",
         "--dump-instantiations",
         "--print-inst-full",
         "--ml-engine",
      ])
      default(setup, "static", static)
      default(setup, "dataname", "data/model")
      assert "dataname" in setup
      trains = Cvc5Trains(setup["dataname"])
      plugs = setup["plugins"]
      plugs.append(trains)
      options = setup["options"]
      if "debug-trains" in options:
         plugs.append(Cvc5TrainsDebug("flatten" in options))
      setup["trains"] = trains
   return solver(setup, Cvc5)

