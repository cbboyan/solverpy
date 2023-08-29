import logging

from . import db
from . import launcher
from ..solver.smt import Cvc5
from ..solver import plugins 
from ..solver.plugins.trains import Cvc5Trains, Cvc5TrainsDebug
from ..builder.cvc5tune import Cvc5Tune

logger = logging.getLogger(__name__)

def cvc5(setup, trains=False):
   def default(key, val):
      if key not in setup:
         setup[key] = val
   def ensure(option):
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
   return setup

def cvc5tune(trains, devels=None, tuneargs=None):
   if "refs" not in trains:
      ref = trains["ref"]
      idx = ref if (type(ref) is int) else 0
      trains["refs"] = [ trains["sidlist"][idx] ]
   trains["builder"] = Cvc5Tune(trains, devels, tuneargs)
   return trains

def launch(setup):
   launcher.init(setup)
   launcher.launch(**setup)
   
   options = setup["options"]
   if ("trains" in setup) and ("compress" in options) and \
      ("no-compress-trains" not in options):
         setup["trains"].compress()

   builder = setup["builder"] if "builder" in setup else None
   if builder:
      builder.build()
      setup["news"] = builder.strategies
      logger.info("New ML strategies:\n" + "\n".join(setup["news"]))
   
   return setup

