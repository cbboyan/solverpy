import logging
import gc

from .. import launcher, db
from ...tools import log
from .common import default
from ...builder.builder import Builder
from .setup import Setup

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


def evaluation(setup: Setup) -> Setup:
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
   if "loops" in setup:
      looping(setup)
   return setup


def oneloop(setup: Setup) -> Setup:

   def is_last(setup):
      return ("loops" in setup) and (setup["it"] == setup["loops"])

   def trains_compress(setup: Setup):
      assert "options" in setup
      options = setup["options"]
      if ("trains" in setup) and ("compress" in options) and \
         ("no-compress-trains" not in options):
         setup["trains"].compress()

   def trains_merge(setup: Setup):
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

   def model_build(setup: Setup):
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
      launcher.launch(**setup)
      trains_compress(setup)
      trains_merge(setup)
   elif "trains" in setup:
      logger.info(
         f"Evaluation skipped.  Starting with data {setup['start_dataname']}")
      setup["trains"].reset(setup["start_dataname"])
   model_build(setup)
   return setup


def launch(setup: Setup, devels: Setup | None = None) -> Setup:

   def do_loop(col):
      if not col: return
      oneloop(col)

   def do_iter(col):
      if not col: return
      #col["sidlist"] = list(setup["refs"]) if "refs" in setup else []
      col["sidlist"].extend(setup["news"] if "news" in setup else [])
      loopinit(col)
      oneloop(col)

   log.ntfy(setup, "solverpy: init")
   launcher.init(setup)
   do_loop(devels)
   do_loop(setup)
   if "loops" in setup:
      assert "it" in setup
      while setup["it"] < setup["loops"]:
         gc.collect()
         log.ntfy(setup, f"solverpy: iter #{setup['it']}")
         do_iter(devels)
         if devels and (setup['it'] + 1 == setup["loops"]):
            # skip evaluation on trains in the last loop if devel is used
            break
         do_iter(setup)
   log.ntfy(setup, "solverpy: done")
   return setup

