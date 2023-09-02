import logging

from . import db
from . import launcher
from ..solver.smt import Cvc5
from ..solver import plugins 
from ..solver.plugins.trains import Cvc5Trains, Cvc5TrainsDebug
from ..builder.cvc5tune import Cvc5Tune
from ..trains import svm

logger = logging.getLogger(__name__)
   

def cvc5(setup, trains=False):
   def default(key, val):
      nonlocal setup
      if key not in setup:
         setup[key] = val
   def ensure(option):
      nonlocal options
      if (option not in options) and (f"no-{option}" not in options):
         options.append(option)

   default("options", ["flatten", "compress"])
   options = setup["options"]
   ensure("flatten") 
   ensure("compress")
   default("limit", "T1")

   if trains:
      static = " ".join([
         "--stats",
         "--stats-internal",
         "--produce-proofs",
         "--produce-models",
         "--dump-instantiations",
         "--print-inst-full",
         "--ml-engine",
      ])
      default("static", static)
   else:
      default("static", "--stats --stats-internal")

   if "plugins" not in setup:
      if "outputs" not in options:
         plugs = plugins.db() 
      else:
         plugs = plugins.outputs(flatten="flatten" in options, 
                                 compress="compress" in options)
      default("plugins", plugs)

   if trains is True:
      default("dataname", "data/model")
      trains = Cvc5Trains(setup["dataname"])
   if trains:
      setup["plugins"].append(trains)
      if "debug-trains" in options:
         setup["plugins"].append(Cvc5TrainsDebug("flatten" in options))
      setup["trains"] = trains      

   solver = Cvc5(setup["limit"], plugins=setup["plugins"], static=setup["static"])
   setup["solver"] = solver
   return setup


def evaluation(setup):
   def default(key, val):
      nonlocal setup
      if key not in setup:
         setup[key] = val

   default("cores", 4)
   default("ref", True)
   default("bidfile", "bids")
   default("sidfile", "sids")
   default("db", db.default())

   if "sidlist" not in setup:
      with open(setup["sidfile"]) as f:
         setup["sidlist"] = f.read().strip().split("\n")
   if "bidlist" not in setup:
      with open(setup["bidfile"]) as f:
         setup["bidlist"] = f.read().strip().split("\n")

   if "loops" in setup:
      setup = looping(setup)
   return setup

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
   setup = loopinit(setup)
   return setup

def cvc5tune(trains, devels=None, tuneargs=None):
   if "refs" not in trains:
      ref = trains["ref"]
      idx = ref if (type(ref) is int) else 0
      trains["refs"] = [ trains["sidlist"][idx] ]
   trains["builder"] = Cvc5Tune(trains, devels, tuneargs)
   return trains

def oneloop(setup):
   def do_compress(setup):
      options = setup["options"]
      if ("trains" in setup) and ("compress" in options) and \
         ("no-compress-trains" not in options):
            setup["trains"].compress()
      return setup
   def do_merge(setup):
      if "previous_trains" in setup:
         f_out = setup["trains"].path(filename="train.in")
         svm.merge(setup["previous_trains"], setup["trains"].path(), f_out=f_out)
         setup["trains"].reset(filename="train.in")
      return setup
   def do_build(setup):
      builder = setup["builder"] if "builder" in setup else None
      if not builder:
         return
      if ("loops" not in setup) or (setup["it"] != setup["loops"]):
         # do not build in the last loop
         builder.build()
         setup["news"] = builder.strategies
         logger.info("New ML strategies:\n" + "\n".join(setup["news"]))

   logger.info(f"Running evaluation loop {setup['it'] if 'it' in setup else 0} on data {setup['dataname'] if 'dataname' in setup else ''}.")
   launcher.launch(**setup)
   do_compress(setup)
   do_merge(setup)
   do_build(setup)
   return setup

def launch(setup, devels=None):
   def do_loop(col):
      if not col: return
      oneloop(col)
   def do_iter(col):
      if not col: return
      col["sidlist"] = list(setup["refs"]) if "refs" in setup else []
      col["sidlist"].extend(setup["news"])
      loopinit(col)
      oneloop(col)

   launcher.init(setup)
   do_loop(devels)
   do_loop(setup)
   if "loops" in setup:
      while setup["it"] < setup["loops"]:
         do_iter(devels)
         do_iter(setup)
   return setup

