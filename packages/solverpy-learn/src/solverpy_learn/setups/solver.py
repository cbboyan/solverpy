import logging
import copy

from solverpy.solver.atp.eprover import E_STATIC, E
from solverpy.solver.plugins.db.sid import Sid
from solverpy.solver.plugins.db.eprovesid import EProverSid
from solverpy.setups.common import default, init, make_solver
from solverpy.setups.setup import Setup
from ..builder.plugins import (
   EnigmaTrains,
   EnigmaMultiTrains,
   EnigmaTrainsDebug,
   Cvc5Trains,
   Cvc5TrainsDebug,
)

logger = logging.getLogger(__name__)


def _eprover_training(setup: Setup) -> Setup:
   """Configure every present Evalset with an E solver and trains plugin."""
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
   ratio = setup["posneg_ratio"]
   chunk_size = setup.get("chunk_size", 1_000_000)
   default(setup, "static", E_STATIC.split())
   assert "static" in setup
   static = setup["static"]
   static.append(f"--training-examples={setup['e_training_examples']}")
   if sel:
      static.append(f'--enigmatic-sel-features="{sel}"')
   if gen:
      static.append(f'--enigmatic-gen-features="{gen}"')
   if not sel and not gen:
      raise ValueError(
         "`sel_features` or `gen_features` must be provided in setup to generate trains."
      )

   init(setup)
   assert "plugins" in setup
   base_plugins = [
      EProverSid() if isinstance(p, Sid) else p
      for p in setup["plugins"]
   ]
   setup["plugins"] = base_plugins
   for key in ("trains", "devels"):
      if key not in setup:
         continue
      evalset = setup[key]
      default(evalset, "dataname", "data/model")
      assert "dataname" in evalset
      dataname = evalset["dataname"]
      if sel and gen:
         plugin = EnigmaMultiTrains(
            dataname,
            sel,
            gen,
            ratio,
            chunk_size=chunk_size,
         )
      elif sel:
         plugin = EnigmaTrains(
            dataname,
            sel,
            "sel",
            ratio,
            chunk_size=chunk_size,
         )
      else:
         plugin = EnigmaTrains(
            dataname,
            gen,
            "gen",
            ratio,
            chunk_size=chunk_size,
         )
      evalset["plugin"] = plugin
      plugins = copy.deepcopy(base_plugins)
      plugins.append(plugin)
      flatten = "flatten" in setup["options"]
      if "debug-trains" in setup["options"]:
         if sel:
            plugins.append(EnigmaTrainsDebug(sel, "sel", flatten, ratio))
         if gen:
            plugins.append(EnigmaTrainsDebug(gen, "gen", flatten, ratio))
      evalset["plugins"] = plugins
      evalset["solver"] = make_solver(setup, E, plugins)
   setup.pop("solver", None)
   return setup


def eprover(setup: Setup) -> Setup:
   assert "trains" in setup
   from solverpy.setups.solver import eprover as _eprover_base
   if not setup.get("sel_features") and not setup.get("gen_features"):
      _eprover_base(setup)
      return setup
   return _eprover_training(setup)


def _cvc5_training(setup: Setup, key: str = "trains") -> Setup:
   """Configure an Evalset in setup[key] with a cvc5 solver and trains plugin."""
   from solverpy.solver.smt.cvc5 import CVC5_STATIC
   default(setup, "static", CVC5_STATIC.split())
   assert "static" in setup
   static = setup["static"]
   if key == "trains":
      static.extend([
         "--produce-proofs",
         "--produce-models",
         "--dump-instantiations",
         "--print-inst-full",
         "--ml-engine",
      ])
   default(setup, "posneg_ratio", 0)
   assert "posneg_ratio" in setup
   ratio = setup["posneg_ratio"]
   chunk_size = setup.get("chunk_size", 1_000_000)
   if key not in setup:
      setup[key] = Evalset()
   evalset = setup[key]
   default(evalset, "dataname", "data/model")
   assert "dataname" in evalset
   dataname = evalset["dataname"]
   plugin = Cvc5Trains(dataname, ratio, chunk_size=chunk_size)
   evalset["plugin"] = plugin
   init(setup)
   plugs = setup["plugins"]
   plugs.append(plugin)
   if key == "trains":
      options = setup["options"]
      if "debug-trains" in options:
         plugs.append(Cvc5TrainsDebug("flatten" in options, ratio))
   from solverpy.setups.solver import cvc5 as _cvc5_base
   _cvc5_base(setup)
   return setup


def cvc5(setup: Setup, training: bool = False, key: str = "trains") -> Setup:
   from solverpy.setups.solver import cvc5 as _cvc5_base
   if not training:
      _cvc5_base(setup)
      return setup
   return _cvc5_training(setup, key)
