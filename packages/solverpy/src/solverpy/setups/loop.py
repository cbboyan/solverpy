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
