import logging

from ...solver import plugins

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
   default(setup, "dataname", "noname")
   
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
   _solver = mk_solver(setup["limit"], **kwargs)
   setup["solver"] = _solver
   return setup

