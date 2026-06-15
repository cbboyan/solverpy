from typing import Callable
import sys
import logging

from ..benchmark import db
from ..benchmark import evaluation as evaluator
from ..report import log
from .common import default
from ..benchmark.path import bids, sids
from .setup import Setup
from .evalset import Evalset
from .runtime import Runtime, initialize
from ..report.talker.evaltalker import EvalTalker

logger = logging.getLogger(__name__)


def experiment(setup: Setup) -> Setup:
   """Normalize a user-facing setup before evaluation or looping starts."""
   if "trains" not in setup:
      if "train" in setup:
         setup["trains"] = Evalset(**setup["train"])
      elif any(k in setup for k in ("benchmarks", "strategies", "refs", "ref",
                                     "bidfile", "sidfile", "dataname")):
         setup["trains"] = Evalset()
      else:
         setup["trains"] = Evalset()

   if "devels" not in setup:
      if "devel" in setup:
         setup["devels"] = Evalset(**setup["devel"])
      elif any(k in setup for k in ("devel_benchmarks", "devel_strategies",
                                    "devel_refs", "devel_ref",
                                    "devel_bidfile", "devel_sidfile",
                                    "devel_dataname")):
         setup["devels"] = Evalset()

   trains = setup.get("trains")
   if trains is not None:
      if "strategies" not in trains:
         if "strategies" in setup:
            trains["strategies"] = setup["strategies"]
         elif "train" in setup and "strategies" in setup["train"]:
            trains["strategies"] = setup["train"]["strategies"]
      if "refs" not in trains and "ref" in setup:
         ref = setup["ref"]
         if isinstance(ref, list):
            trains["refs"] = ref
         elif ref is not None:
            trains["refs"] = [ref]
      if "benchmarks" not in trains and "benchmarks" in setup:
         trains["benchmarks"] = setup["benchmarks"]
      if "dataname" not in trains and "dataname" in setup:
         trains["dataname"] = setup["dataname"]
      if "start_dataname" not in trains and "start_dataname" in setup:
         trains["start_dataname"] = setup["start_dataname"]

   devels = setup.get("devels")
   if devels is not None:
      if "strategies" not in devels:
         if "devel_strategies" in setup:
            devels["strategies"] = setup["devel_strategies"]
         elif "strategies" in setup and "devel" in setup:
            devels["strategies"] = setup["strategies"]
      if "refs" not in devels:
         if "devel_refs" in setup:
            devels["refs"] = setup["devel_refs"]
         elif "ref" in setup:
            ref = setup["ref"]
            if isinstance(ref, list):
               devels["refs"] = ref
            elif ref is not None:
               devels["refs"] = [ref]
      if "benchmarks" not in devels:
         if "devel_benchmarks" in setup:
            devels["benchmarks"] = setup["devel_benchmarks"]
         elif "benchmarks" in setup and "devel" in setup:
            devels["benchmarks"] = setup["benchmarks"]
      if "dataname" not in devels:
         if "devel_dataname" in setup:
            devels["dataname"] = setup["devel_dataname"]
         elif "dataname" in setup and "devel" in setup:
            devels["dataname"] = setup["dataname"]
      if "start_dataname" not in devels and "devel_start_dataname" in setup:
         devels["start_dataname"] = setup["devel_start_dataname"]
   return setup


def evaluation(setup: Setup) -> Setup:
   experiment(setup)

   def configure_evalset(evalset: Evalset) -> None:
      default(evalset, "ref", True)
      if "strategies" not in evalset:
         default(evalset, "sidfile", "sids")
         with open(evalset["sidfile"]) as f:
            evalset["strategies"] = f.read().strip().split("\n")
      if "benchmarks" not in evalset:
         default(evalset, "bidfile", "bids")
         with open(evalset["bidfile"]) as f:
            evalset["benchmarks"] = f.read().strip().split("\n")

   def check_list(evalset: Evalset, key: str, fun: Callable) -> None:
      if key not in evalset:
         return
      for id in evalset[key]:
         try:
            fun(id)
         except Exception as e:
            logger.error(f"Wrong id in {key}: {id}")
            logger.error(f"Exception: {e}")
            sys.exit(0)

   default(setup, "cores", 4)
   default(setup, "delfix", None)
   assert "delfix" in setup
   default(setup, "db", db.default(delfix=setup["delfix"]))
   default(setup, "ntfy", None)

   for key in ("trains", "devels"):
      if key not in setup:
         continue
      evalset = setup[key]
      configure_evalset(evalset)
      check_list(evalset, "strategies", sids.load)
      check_list(evalset, "refs", sids.load)
      check_list(evalset, "benchmarks", bids.problems)
   return setup


def boot(setup: Setup) -> Runtime:
   assert "options" in setup
   talker = EvalTalker(headless="headless" in setup["options"])
   runtime = initialize(setup)
   talker._log_queue = runtime.log_queue
   talker.log_start()
   setup["talker"] = talker
   return runtime


def launch(setup: Setup) -> Setup | None:
   experiment(setup)
   runtime = None
   try:
      log.ntfy(setup, "solverpy: init")
      evaluator.init(setup)
      runtime = boot(setup)
      assert "trains" in setup
      evaluator.launch(setup["trains"], **setup)
      log.ntfy(setup, "solverpy: done")
      return setup
   except KeyboardInterrupt:
      logger.warning("Terminated (keyboard interrupt)")
      print("Terminated (keyboard interrupt)")
      sys.exit(0)
   finally:
      if runtime:
         setup["talker"].log_stop()
         runtime.shutdown()
