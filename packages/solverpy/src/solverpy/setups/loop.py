from typing import Callable
import sys
import logging

from ..benchmark import db
from ..benchmark import evaluation as evaluator
from ..tools import log
from .common import default
from ..benchmark.path import bids, sids
from .setup import Setup
from ..task.solvertalker import SolverTalker
from ..task.logtalker import LogTalker

logger = logging.getLogger(__name__)


def evaluation(setup: Setup) -> Setup:

   def check_list(setup: Setup, key: str, fun: Callable) -> None:
      if key not in setup:
         return
      for id in setup[key]:
         try:
            fun(id)
         except Exception as e:
            logger.error(f"Wrong id in {key}: {id}")
            logger.error(f"Exception: {e}")
            sys.exit(0)

   default(setup, "cores", 4)
   default(setup, "ref", True)
   default(setup, "bidfile", "bids")
   assert "bidfile" in setup
   default(setup, "sidfile", "sids")
   assert "sidfile" in setup
   default(setup, "delfix", None)
   assert "delfix" in setup
   default(setup, "db", db.default(delfix=setup["delfix"]))
   default(setup, "ntfy", None)
   if "sidlist" not in setup:
      with open(setup["sidfile"]) as f:
         setup["sidlist"] = f.read().strip().split("\n")
   if "bidlist" not in setup:
      with open(setup["bidfile"]) as f:
         setup["bidlist"] = f.read().strip().split("\n")
   check_list(setup, "sidlist", sids.load)
   check_list(setup, "refs", sids.load)
   check_list(setup, "bidlist", bids.problems)
   return setup


def launch(setup: Setup, devels: Setup | None = None) -> Setup | None:
   try:
      log.ntfy(setup, "solverpy: init")
      evaluator.init(setup)
      if "headless" in setup.get("options", []):
         talker = LogTalker()
      else:
         talker = SolverTalker()
      evaluator.launch(talker=talker, **setup)
      log.ntfy(setup, "solverpy: done")
      return setup
   except KeyboardInterrupt:
      print("Terminated (keyboard interrupt)")
      sys.exit(0)
