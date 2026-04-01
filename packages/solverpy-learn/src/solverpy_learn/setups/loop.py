from typing import Callable
import sys
import logging
import gc

from solverpy.benchmark import db
from solverpy.benchmark import evaluation as evaluator
from solverpy.tools import log
from solverpy.setups.common import default
from solverpy.benchmark.path import bids, sids
from solverpy.setups.setup import Setup
from solverpy.task.solvertalker import SolverTalker
from solverpy.task.logtalker import LogTalker
from ..builder.builder import Builder

logger = logging.getLogger(__name__)


def loopinit(setup: Setup) -> Setup:
   assert "basedataname" in setup
   assert "trains" in setup
   base = setup["basedataname"]
   if "it" not in setup:
      setup["it"] = 0
      filename = "train.in"
   else:
      setup["it"] += 1
      setup["previous_trains"] = setup["trains"].path()
      filename = "addon.in"
   it = setup["it"]
   setup["dataname"] = f"{base}/loop{it:02d}"
   setup["trains"].reset(setup["dataname"], filename)
   if "builder" in setup:
      builder: Builder = setup["builder"]
      builder.reset(setup["dataname"])
   return setup


def looping(setup: Setup) -> Setup:
   assert "dataname" in setup
   setup["basedataname"] = setup["dataname"]
   default(setup, "max_proofs", 0)
   assert "max_proofs" in setup
   if setup["max_proofs"] > 0:
      setup["proofs"] = {}
   loopinit(setup)
   return setup


def oneloop(setup: Setup) -> Setup:

   assert "options" in setup
   options = setup["options"]

   def is_last(setup: Setup) -> bool:
      return ("loops" in setup) and (setup.get("it") == setup["loops"])

   def trains_compress(setup: Setup) -> None:
      nonlocal options
      if ("trains" in setup) and ("compress" in options) and \
         ("no-compress-trains" not in options):
         setup["trains"].compress()

   def trains_merge(setup: Setup) -> None:
      assert "trains" in setup
      trains = setup["trains"]
      if ("previous_trains" not in setup) or is_last(setup):
         return
      previous = setup["previous_trains"]
      if not trains.exists():
         logger.warning(f"No trains found: {trains.path()}.")
         logger.warning(f"Reusing previous trains: {previous}.")
         trains.link(previous)
         if "max_proofs" in setup and setup["max_proofs"] > 0:
            setup["max_proofs"] += 1
            logger.info(f"Increasing max_proofs to: {setup['max_proofs']}")
      trains.merge(setup["previous_trains"], "train.in")
      trains.reset(filename="train.in")

   def model_build(setup: Setup) -> None:
      if "builder" not in setup:
         return
      builder = setup["builder"]
      if builder and not is_last(setup):
         builder.build()
         setup["news"] = builder.strategies
         logger.info("New ML strategies:\n" + "\n".join(setup["news"]))

   assert "dataname" in setup
   it = setup['it'] if 'it' in setup else 0
   logger.info(
      f"Running evaluation loop {it} on data {setup['dataname']}.\n> \n> ## Evaluation `{setup['dataname']}` ##\n> "
   )
   if (it > 0) or ("start_dataname" not in setup):
      if "headless" in options:
         talker = LogTalker()
      else:
         talker = SolverTalker()
      evaluator.launch(talker=talker, **setup)
      if "trains" not in setup:
         return setup
      trains_compress(setup)
      trains_merge(setup)
   elif "trains" in setup:
      logger.info(
         f"Evaluation skipped.  Starting with data {setup['start_dataname']}")
      setup["trains"].reset(setup["start_dataname"])
   model_build(setup)
   return setup


def launch(setup: Setup, devels: Setup | None = None) -> Setup | None:

   def do_loop(col: Setup | None) -> None:
      if not col: return
      oneloop(col)

   def do_iter(col: Setup | None) -> None:
      if not col: return
      col["sidlist"].extend(setup["news"] if "news" in setup else [])
      loopinit(col)
      oneloop(col)

   try:
      log.ntfy(setup, "solverpy: init")
      evaluator.init(setup)
      if "loops" in setup:
         looping(setup)
         if devels:
            looping(devels)
      do_loop(devels)
      do_loop(setup)
      if "loops" in setup:
         while setup["it"] < setup["loops"]:
            gc.collect()
            log.ntfy(setup, f"solverpy: iter #{setup['it']}")
            do_iter(devels)
            if devels and (setup['it'] + 1 == setup["loops"]):
               break
            do_iter(setup)
      log.ntfy(setup, "solverpy: done")
      return setup
   except KeyboardInterrupt:
      print("Terminated (keyboard interrupt)")
      sys.exit(0)
