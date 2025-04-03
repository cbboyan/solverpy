import logging

from .. import launcher, db
from ...tools import log
from ...builder import svm
from .common import default

logger = logging.getLogger(__name__)

def loopinit(setup):
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
      setup["builder"].reset(setup["dataname"])
   return setup

def looping(setup):
   setup["basedataname"] = setup["dataname"]
   loopinit(setup)
   return setup

def evaluation(setup):
   default(setup, "cores", 4)
   default(setup, "ref", True)
   default(setup, "bidfile", "bids")
   default(setup, "sidfile", "sids")
   default(setup, "db", db.default())
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

def oneloop(setup):
   def is_last(setup):
      return ("loops" in setup) and (setup["it"] == setup["loops"])
   def trains_compress(setup):
      options = setup["options"]
      if ("trains" in setup) and ("compress" in options) and \
         ("no-compress-trains" not in options):
            setup["trains"].compress()
   def trains_merge(setup):
      if ("previous_trains" in setup) and not is_last(setup):
         setup["trains"].merge(setup["previous_trains"], "train.in")
         #f_out = setup["trains"].path(filename="train.in")
         #svm.merge(setup["previous_trains"], setup["trains"].path(), f_out=f_out)
         setup["trains"].reset(filename="train.in")
   def model_build(setup):
      builder = setup["builder"] if "builder" in setup else None
      if builder and not is_last(setup):
         builder.build()
         setup["news"] = builder.strategies
         logger.info("New ML strategies:\n" + "\n".join(setup["news"]))

   it = setup['it'] if 'it' in setup else 0
   logger.info(f"Running evaluation loop {it} on data {setup['dataname']}.\n> \n> ## Evaluation `{setup['dataname']}` ##\n> ")
   if (it > 0) or ("start_dataname" not in setup):
      launcher.launch(**setup)
      trains_compress(setup)
      trains_merge(setup)
   elif "trains" in setup: 
      logger.info(f"Evaluation skipped.  Starting with data {setup['start_dataname']}")
      setup["trains"].reset(setup["start_dataname"])
   model_build(setup)
   return setup

def launch(setup, devels=None):
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
      while setup["it"] < setup["loops"]:
         log.ntfy(setup, f"solverpy: iter #{setup['it']}")
         do_iter(devels)
         if devels and (setup['it']+1 == setup["loops"]):
            # skip evaluation on trains in the last loop if devel is used
            break
         do_iter(setup)
   log.ntfy(setup, "solverpy: done")
   return setup

