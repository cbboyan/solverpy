import logging

from . import db
from . import launcher
from ..builder.cvc5tune import Cvc5Tune
from ..solver.smt import Cvc5 as SmtCvc5
from ..solver.smt.cvc5 import CVC5_BINARY, CVC5_STATIC # == "cvc5"
from ..solver.atp.eprover import E_STATIC # == "cvc5"
from ..solver.atp import Cvc5 as TptpCvc5
from ..solver import plugins 
from ..solver.plugins.trains import Cvc5Trains, Cvc5TrainsDebug
from ..solver.plugins.trains import EnigmaTrains, EnigmaTrainsDebug
from ..trains import svm
from ..tools import log
from ..solver.atp.eprover import E
from ..solver.atp.vampire import Vampire
from ..solver.atp.prover9 import Prover9

logger = logging.getLogger(__name__)

# generic arguments accepted by solver constructors
GENERICS = frozenset(["binary", "plugins", "static", "complete"])

def default(setup, key, val):
   if key not in setup:
      setup[key] = val

def ensure(options, option):
   baseopt = option if not option.startswith("no-") else option[3:]
   if (baseopt not in options) and (f"no-{baseopt}" not in options):
      options.append(option)

def init(setup):
   default(setup, "options", ["flatten", "compress"])
   options = setup["options"]
   ensure(options, "flatten") 
   ensure(options, "compress")
   default(setup, "limit", "T1")
   
   if "plugins" not in setup:
      if "outputs" not in options:
         plugs = plugins.db() 
      else:
         plugs = plugins.outputs(flatten="flatten" in options, 
                                 compress="compress" in options)
      default(setup, "plugins", plugs)
   return setup

def solver(setup, mk_solver):
   kwargs = {x:setup[x] for x in setup if x in GENERICS}
   solver = mk_solver(setup["limit"], **kwargs)
   setup["solver"] = solver
   return setup

def eprover(setup, trains=False):
   init(setup)   
   if trains:
      default(setup, "sel_features", "C(l,v,h,s,c,d,a)")
      default(setup, "e_training_examples", "11")
      default(setup, "static", E_STATIC)
      setup["static"] += " ".join(["", # make a space
         f"--training-examples={setup['e_training_examples']}",
         f"--enigmatic-sel-features=\"{setup['sel_features']}\"",
      ])
      default(setup, "dataname", "data/model")
      trains = EnigmaTrains(setup["dataname"], setup["sel_features"])
      plugs = setup["plugins"]
      plugs.append(trains)
      if "debug-trains" in setup["options"]:
         plugs.append(EnigmaTrainsDebug( setup["sel_features"], "flatten" in setup["options"]))
      setup["trains"] = trains
   return solver(setup, E)

def vampire(setup):
   init(setup)   
   return solver(setup, Vampire)

def prover9(setup):
   init(setup)   
   return solver(setup, Prover9)

def cvc5(setup, trains=False, tptp=False):
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
   default("binary", CVC5_BINARY)

   if trains:
      static = CVC5_STATIC + " ".join([
         "--produce-proofs",
         "--produce-models",
         "--dump-instantiations",
         "--print-inst-full",
         "--ml-engine",
      ])
      default("static", static)
   else:
      default("static", CVC5_STATIC)

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

   Cvc5 = TptpCvc5 if tptp else SmtCvc5
   solver = Cvc5(setup["limit"], binary=setup["binary"], plugins=setup["plugins"], static=setup["static"])
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
   default("ntfy", None)

   if "sidlist" not in setup:
      with open(setup["sidfile"]) as f:
         setup["sidlist"] = f.read().strip().split("\n")
   if "bidlist" not in setup:
      with open(setup["bidfile"]) as f:
         setup["bidlist"] = f.read().strip().split("\n")

   if "loops" in setup:
      looping(setup)
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
   loopinit(setup)
   return setup

def cvc5tune(trains, devels=None, tuneargs=None):
   if "refs" not in trains:
      ref = trains["ref"] 
      idx = ref if (type(ref) is int) else 0
      trains["refs"] = [ trains["sidlist"][idx] ]
   trains["builder"] = Cvc5Tune(trains, devels, tuneargs)
   return trains

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
         f_out = setup["trains"].path(filename="train.in")
         svm.merge(setup["previous_trains"], setup["trains"].path(), f_out=f_out)
         setup["trains"].reset(filename="train.in")
   def model_build(setup):
      builder = setup["builder"] if "builder" in setup else None
      if builder and not is_last(setup):
         builder.build()
         setup["news"] = builder.strategies
         logger.info("New ML strategies:\n" + "\n".join(setup["news"]))

   logger.info(f"Running evaluation loop {setup['it'] if 'it' in setup else 0} on data {setup['dataname'] if 'dataname' in setup else ''}.")
   launcher.launch(**setup)
   trains_compress(setup)
   trains_merge(setup)
   model_build(setup)
   return setup

def launch(setup, devels=None):
   def do_loop(col):
      if not col: return
      oneloop(col)
   def do_iter(col):
      if not col: return
      col["sidlist"] = list(setup["refs"]) if "refs" in setup else []
      col["sidlist"].extend(setup["news"] if "news" in setup else [])
      loopinit(col)
      oneloop(col)

   log.ntfy(setup, f"solverpy: init")
   launcher.init(setup)
   do_loop(devels)
   do_loop(setup)
   if "loops" in setup:
      while setup["it"] < setup["loops"]:
         log.ntfy(setup, f"solverpy: iter #{setup['it']}")
         do_iter(devels)
         do_iter(setup)
   log.ntfy(setup, f"solverpy: done")
   return setup

