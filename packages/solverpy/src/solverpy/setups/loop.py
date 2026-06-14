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


def evaluation(setup: Setup) -> Setup:

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

   # Initialize trains Evalset
   if "trains" not in setup:
      setup["trains"] = Evalset()
   trains = setup["trains"]

   default(trains, "ref", True)
   if "strategies" not in trains:
      default(trains, "sidfile", "sids")
      with open(trains["sidfile"]) as f:
         trains["strategies"] = f.read().strip().split("\n")
   if "benchmarks" not in trains:
      default(trains, "bidfile", "bids")
      with open(trains["bidfile"]) as f:
         trains["benchmarks"] = f.read().strip().split("\n")
   check_list(trains, "strategies", sids.load)
   check_list(trains, "refs", sids.load)
   check_list(trains, "benchmarks", bids.problems)
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
