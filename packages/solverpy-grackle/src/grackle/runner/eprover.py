from solverpy.solver.atp.eprover import E, E_BINARY, E_STATIC

from .solverpy import SolverPyRunner
from grackle.trainer.eprover.heuristic import HEURISTIC_CEFS


E_FIXED_ARGS = "--delete-bad-limit=150000000 "

DEFAULTS = {
   "sel": "SelectMaxLComplexAvoidPosPred",
   "tord": "LPO4",
   "tord_prec": "arity",
   "tord_weight": "arity",
   "simparamod": "none",
   "srd": "0",
   "forwardcntxtsr": "0",
   "splaggr": "0",
   "splcl": "0",
   "tord_const": "0",
   "sine": "0",
   "defcnf": "24",
   "prefer": "0",
   "fwdemod": "2",
   "der": "none",
   "presat": "0",
   "condense": "0",
}

SINE_DEFAULTS = {
   "sineG": "CountFormulas",
   "sineh": "hypos",
   "sinegf": "1.2",
   "sineD": "none",
   "sineR": "none",
   "sineL": "100",
   "sineF": "1.0",
}

E_PROTO_ARGS = "%(splaggr)s%(srd)s%(forwardcntxtsr)s%(defcnf)s%(prefer)s%(presat)s%(condense)s%(splcl)s%(fwdemod)s%(der)s%(simparamod)s-t%(tord)s %(prord)s-W%(sel)s %(sine)s%(heur)s"

E_SINE_ARGS = "--sine='GSinE(%(sineG)s,%(sineh)s,%(sinegf)s,%(sineD)s,%(sineR)s,%(sineL)s,%(sineF)s)' "


def cef2block(cef):
   "Encode a CEF as a ParamILS string containg only [a-zA-Z0-9_]."
   return cef.replace("-","_M_").replace(",","__").replace(".","_D_").replace("(","__").replace(")","")

def block2cef(block):
   "Decode a CEF from a ParamILS string."
   parts = block.replace("_M_","-").replace("_D_",".").split("__")
   return "%s(%s)" % (parts[0], ",".join(parts[1:]))

def convert(params):
   # conversion from old ordering version
   if "prord" in params:
      params = dict(params)
      params["tord_prec"] = params["prord"]
      if params["tord"] == "KBO6":
         params["tord_weight"] = "invfreqrank"
         params["tord_const"] = "1"
      if params["tord"] == "WPO":
         params["tord_weight"] = "invfreqrank"
         params["tord_const"] = "1"
         params["tord_coefs"] = "constant"
         params["tord_algebra"] = "Sum"
      del params["prord"]
   # handle old sine version
   if "sine" in params and params["sine"] == "1":
      if params["sineR"] == "UU":
         params["sineR"] = "none"
      defaults = dict(SINE_DEFAULTS)
      defaults.update(params)
      params = defaults
   else:
      params["sine"] = "0"
   # add missing defaults
   defaults = dict(DEFAULTS)
   defaults.update(params)
   params = defaults
   return params


class EproverRunner(SolverPyRunner):

   RESOURCE_KEY = "Processed"

   def __init__(self, config={}):
      SolverPyRunner.__init__(self, config)
      self.default("penalty", 1000000)
      self.config["prefix"] = "eprover-"
      binary = self.config.get("ebinary") or E_BINARY
      static = self.config.get("eargs") or E_STATIC
      limit = self.config["timeout"]
      self._solver = E(limit=f"T{limit}", binary=binary, static=static)

   def args(self, params):
      eargs = dict(params)
      eargs = convert(eargs)

      def simple(arg, option):
         nonlocal eargs
         eargs[arg] = option if eargs[arg] == "1" else ""

      def direct(arg, option, none):
         nonlocal eargs
         if eargs[arg] == none:
            eargs[arg] = ""
         else:
            eargs[arg] = "%s=%s " % (option, eargs[arg])

      # simple binary flags (no value)
      simple("splaggr",        "--split-aggressive ")
      simple("srd",            "--split-reuse-defs ")
      simple("forwardcntxtsr", "--forward-context-sr ")
      simple("prefer",         "--prefer-initial-clauses ")
      simple("presat",         "--presat-simplify ")
      simple("condense",       "--condense ")

      # direct valued flags
      direct("defcnf",  "--definitional-cnf", "none")
      direct("splcl",   "--split-clauses",       "0")
      direct("fwdemod", "--forward-demod-level", "2")

      # destructive equality resolution
      if eargs["der"] == "std":
         eargs["der"] = "--destructive-er "
      elif eargs["der"] == "strong":
         eargs["der"] = "--destructive-er --strong-destructive-er "
      elif eargs["der"] == "agg":
         eargs["der"] = "--destructive-er --destructive-er-aggressive "
      elif eargs["der"] == "stragg":
         eargs["der"] = "--destructive-er --destructive-er-aggressive --strong-destructive-er "
      else: # should be "none"
         eargs["der"] = ""

      # paramodulation
      if eargs["simparamod"] == "normal":
         eargs["simparamod"] = "--simul-paramod "
      elif eargs["simparamod"] == "oriented":
         eargs["simparamod"] = "--oriented-simul-paramod "
      else: # should be "none"
         eargs["simparamod"] = ""

      # term ordering
      if eargs["tord"] == "KBO6":
         eargs["prord"] = "-G%(tord_prec)s -w%(tord_weight)s " % eargs
         if eargs["tord_const"] != "0":
            eargs["prord"] += "-c%(tord_const)s " % eargs
      elif eargs["tord"] == "LPO4":
         eargs["prord"] = "-G%(tord_prec)s " % eargs
      elif eargs["tord"] == "WPO":
         eargs["prord"] = "-G%(tord_prec)s -w%(tord_weight)s -A%(tord_coefs)s -a%(tord_algebra)s " % eargs
         if eargs["tord_const"] != "0":
            eargs["prord"] += " -c%(tord_const)s " % eargs
      else:
         eargs["prord"] = ""

      # SinE
      if eargs["sine"] == "1":
         for x in eargs:
            if x.startswith("sine") and eargs[x] == "none":
               eargs[x] = ""
         eargs["sine"] = E_SINE_ARGS % eargs
      else:
         eargs["sine"] = ""

      # given clause selection heuristic
      if "heur0" in eargs:
         # new indexed format: heur{i} is an index into HEURISTIC_CEFS
         # always append FIFOWeight(ConstPrio) as the last CEF to ensure completeness
         slots = int(eargs["slots"])
         cefs = ["%s*%s" % HEURISTIC_CEFS[int(eargs["heur%d" % i])] for i in range(slots)]
         cefs.append("1*FIFOWeight(ConstPrio)")
         eargs["heur"] = "-H'(%s)'" % ",".join(cefs)
      else:
         # old block-encoded format: freq{i} + cef{i}
         slots = int(eargs["slots"])
         cefs = []
         for i in range(slots):
            cefs += ["%s*%s" % (eargs["freq%d"%i], block2cef(eargs["cef%d"%i]))]
         cefs.sort(key=lambda x: int(x.split("*")[0]))
         eargs["heur"] = "-H'(%s)'" % ",".join(cefs)

      # new optional args (absent from DEFAULTS; use .get() with E-default fallbacks)
      ho_extra = ""
      if eargs.get("strong_rw_inst", "0") == "1":
         ho_extra += "--strong-rw-inst "
      if eargs.get("no_eq_unfolding", "0") == "1":
         ho_extra += "--no-eq-unfolding "
      if eargs.get("sos_input_types", "0") == "1":
         ho_extra += "--sos-uses-input-types "
      neg_ext = eargs.get("neg_ext", "off")
      if neg_ext != "off":
         ho_extra += "--neg-ext=%s " % neg_ext
      pos_ext = eargs.get("pos_ext", "off")
      if pos_ext != "off":
         ho_extra += "--pos-ext=%s " % pos_ext
      ext_sup = eargs.get("ext_sup_max_depth", "-1")
      if ext_sup != "-1":
         ho_extra += "--ext-sup-max-depth=%s " % ext_sup
      if eargs.get("lift_lambdas", "true") != "true":
         ho_extra += "--lift-lambdas=false "
      if eargs.get("local_rw", "false") == "true":
         ho_extra += "--local-rw=true "
      if eargs.get("fool_unroll", "true") != "true":
         ho_extra += "--fool-unroll=false "
      if eargs.get("inverse_recognition", "false") == "true":
         ho_extra += "--inverse-recognition "
      if eargs.get("replace_inj_defs", "false") == "true":
         ho_extra += "--replace-inj-defs "
      ho_ord = eargs.get("ho_order_kind", "lfho")
      if ho_ord != "lfho":
         ho_extra += "--ho-order-kind=%s " % ho_ord

      sat_extra = ""
      satcheck = eargs.get("satcheck", "none")
      if satcheck != "none":
         sat_extra = "--satcheck=%s --satcheck-proc-interval=5000 " % satcheck

      return E_FIXED_ARGS + (E_PROTO_ARGS % eargs) + ho_extra + sat_extra

   def clean(self, params):
      params = convert(params)

      if "slots" not in params:
         return None
      params = dict(params)
      slots = int(params["slots"])
      delete = []
      for param in params:
         if param.startswith("freq") or param.startswith("cef"):
            n = int(param.lstrip("freqcef"))
            if n >= slots:
               delete.append(param)
         elif param.startswith("heur") and param[4:].isdigit():
            n = int(param[4:])
            if n >= slots:
               delete.append(param)

      if "sine" in params and params["sine"] == "0":
         delete.extend(SINE_DEFAULTS)

      if "prord" not in params:
         if params["tord"] == "Auto":
            delete.extend(["tord_prec", "tord_weight", "tord_const", "tord_algebra", "tord_coefs"])
         elif params["tord"] == "LPO4":
            delete.extend(["tord_weight", "tord_const", "tord_algebra", "tord_coefs"])
         elif params["tord"] == "KBO6":
            delete.extend(["tord_algebra", "tord_coefs"])

      for param in delete:
         if param in params:
            del params[param]

      return params
