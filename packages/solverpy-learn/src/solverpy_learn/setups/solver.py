import logging
import copy

from solverpy.solver.atp.eprover import E_STATIC, E
from solverpy.solver.plugins.db.sid import Sid
from solverpy.solver.plugins.db.eprovesid import EProverSid
from solverpy.setups.common import default, init, make_solver
from solverpy.setups.setup import Setup
from solverpy.setups.evalset import Evalset
from solverpy.solver.smt.cvc5 import CVC5_STATIC, Cvc5
from ..builder.plugins import (
   EnigmaTrains,
   EnigmaMultiTrains,
   EnigmaTrainsDebug,
   Cvc5Trains,
   Cvc5TrainsDebug,
)

logger = logging.getLogger(__name__)


def _append_missing(static: list[str], options: list[str]) -> None:
   for option in options:
      if option not in static:
         static.append(option)


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
   training_static = [f"--training-examples={setup['e_training_examples']}"]
   if sel:
      training_static.append(f'--enigmatic-sel-features="{sel}"')
   if gen:
      training_static.append(f'--enigmatic-gen-features="{gen}"')
   if not sel and not gen:
      raise ValueError(
         "`sel_features` or `gen_features` must be provided in setup to generate trains."
      )

   init(setup)
   assert "options" in setup
   assert "plugins" in setup
   base_plugins = [
      EProverSid() if isinstance(p, Sid) else p
      for p in setup["plugins"]
   ]
   setup["plugins"] = base_plugins
   for key in ("evals", "devels"):
      if key not in setup:
         continue
      evalset = setup[key]
      default(evalset, "limit", "T1")
      default(evalset, "static", E_STATIC.split())
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
      evalset["static"] = list(evalset["static"])
      _append_missing(evalset["static"], training_static)
      evalset["solver"] = make_solver(
         evalset,
         E,
         plugins,
         reloader=setup.get("reloader", False),
         options=setup["options"],
      )
   setup.pop("solver", None)
   return setup


def eprover(setup: Setup) -> Setup:
   assert "evals" in setup
   from solverpy.setups.solver import eprover as _eprover_base
   if not setup.get("sel_features") and not setup.get("gen_features"):
      _eprover_base(setup)
      return setup
   return _eprover_training(setup)


def _ensure_cvc5_training_static(evalset: Evalset) -> None:
   default(evalset, "static", CVC5_STATIC.split())
   assert "static" in evalset
   evalset["static"] = list(evalset["static"])
   _append_missing(evalset["static"], [
      "--produce-proofs",
      "--produce-models",
      "--dump-instantiations",
      "--print-inst-full",
      "--ml-engine",
   ])


def _cvc5_training(setup: Setup, key: str = "evals") -> Setup:
   """Configure an Evalset in setup[key] with a cvc5 solver and trains plugin."""
   default(setup, "posneg_ratio", 0)
   assert "posneg_ratio" in setup
   ratio = setup["posneg_ratio"]
   chunk_size = setup.get("chunk_size", 1_000_000)
   if key not in setup:
      setup[key] = Evalset()
   evalset = setup[key]
   default(evalset, "limit", "T1")
   _ensure_cvc5_training_static(evalset)
   default(evalset, "dataname", "data/model")
   assert "dataname" in evalset
   dataname = evalset["dataname"]
   plugin = Cvc5Trains(dataname, ratio, chunk_size=chunk_size)
   evalset["plugin"] = plugin
   init(setup)
   assert "options" in setup
   assert "plugins" in setup
   plugs = copy.deepcopy(setup["plugins"])
   plugs.append(plugin)
   options = setup["options"]
   if "debug-trains" in options:
      plugs.append(Cvc5TrainsDebug("flatten" in options, ratio))
   evalset["plugins"] = plugs
   evalset["solver"] = make_solver(
      evalset,
      Cvc5,
      plugs,
      reloader=setup.get("reloader", False),
      options=setup["options"],
   )
   setup.pop("solver", None)
   return setup


def cvc5(setup: Setup, key: str | None = None) -> Setup:
   if key is not None:
      return _cvc5_training(setup, key)
   for evalset_key in ("evals", "devels"):
      if evalset_key in setup:
         _cvc5_training(setup, evalset_key)
   return setup
