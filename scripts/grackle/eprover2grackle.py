#!/usr/bin/env python3

import sys
from grackle.runner.eprover import cef2block, EproverRunner

# Grackle's (BliStr-based) parameter space for E strategies:
#
# (base)
#
# sel {SelectMaxLComplexAvoidPosPred,SelectNewComplexAHP,SelectComplexG,SelectCQPrecWNTNp} [SelectMaxLComplexAvoidPosPred]
# simparamod {none,normal,oriented} [normal]
# srd {0,1} [0]
# forwardcntxtsr {0,1} [1]
# splaggr {0,1} [1]
# splcl {0,4,7} [4]
#
# (order)
#
# tord {Auto,LPO4,KBO6} [LPO4]
# tord_prec {unary_first,unary_freq,arity,invarity,const_max,const_min,freq,invfreq,invconjfreq,invfreqconjmax,invfreqconjmin,invfreqconstmin} [arity]
# tord_weight {firstmaximal0,arity,aritymax0,modarity,modaritymax0,aritysquared,aritysquaredmax0,invarity,invaritymax0,invaritysquared,invaritysquaredmax0,precedence,invprecedence,precrank5,precrank10,precrank20,freqcount,invfreqcount,freqrank,invfreqrank,invconjfreqrank,freqranksquare,invfreqranksquare,invmodfreqrank,invmodfreqrankmax0,constant} [arity]
# tord_const {0,1} [0]
#
# CONDITIONS: tord_prec only for LPO4,KBO6; tord_weight,tord_const only for KBO6
#
# (sine)
#
# sineG {CountFormulas,CountTerms} [CountFormulas]
# sineh {none,hypos} [hypos]
# sinegf {1.1,1.2,1.4,1.5,2.0,5.0,6.0} [1.2]
# sineD {none,1,3,10,20,40,160} [none]
# sineR {none,01,02,03,04} [none]
# sineL {10,20,40,60,80,100,500,20000} [100]
# sineF {1.0,0.8,0.6} [1.0]
#
#

# (NEW)
#
# defcnf   {0,1}   [0]                 # --definitional-cnf
# prefer   {0,1}   [1]                 # --prefer-initial-clauses
# fwdemod  {0,1,2} [2]                 # --forward-demod-level=<val> (2 when none)
# der      {none,std,strong,agg} [none]
# presat   {0,1}   [0]                 # --presat-simplify
# condense {0,1}   [0]
#
#

defaults = {
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
   "defcnf": "0",
   "prefer": "0",
   "fwdemod": "2",
   "der": "none",
   "presat": "0",
   "condense": "0",
}

#
shotcuts = {
   "W": "literal-selection-strategy",
   "t": "term-ordering",
   "G": "order-precedence-generation",
   "w": "order-weight-generation",
   "c": "order-constant-weight",
   "F": "forward-demod-level",
   "H": "define-heuristic",
}

supported = {
   "literal-selection-strategy": [
      "SelectMaxLComplexAvoidPosPred",
      "SelectNewComplexAHP",
      "SelectComplexG",
      "SelectCQPrecWNTNp",
      "SelectMaxLComplexAPPNTNp",
      "SelectNewComplexAHPNS",
      "SelectNewComplexAHPExceptRRHorn",
      "PSelectComplexExceptRRHorn",
      "SelectComplexAHPExceptRRHorn",
      "SelectComplexAHP",
      "SelectComplexExceptRRHorn",
      "SelectCQArNpEqFirst",
      "SelectCQArNTEqFirst",
      "SelectCQArNTEqFirstUnlessPDom",
      "SelectCQArNTNpEqFirst",
      "SelectCQIPrecWNTNp",
      "SelectLargestNegLit",
      "SelectNegativeLiterals",
      "SelectNewComplexAHPExceptUniqMaxHorn",
      "NoSelection",
   ],
   "term-ordering": [
      "Auto",
      "LPO4",
      "KBO6"
   ],
   "order-precedence-generation": [
      "unary_first",
      "unary_freq",
      "arity",
      "invarity",
      "const_max",
      "const_min",
      "freq",
      "invfreq",
      "invconjfreq",
      "invfreqconjmax",
      "invfreqconjmin",
      "invfreqconstmin"
   ],
   "order-weight-generation": [
      "firstmaximal0",
      "arity",
      "aritymax0",
      "modarity",
      "modaritymax0",
      "aritysquared",
      "aritysquaredmax0",
      "invarity",
      "invaritymax0",
      "invaritysquared",
      "invaritysquaredmax0",
      "precedence",
      "invprecedence",
      "precrank5",
      "precrank10",
      "precrank20",
      "freqcount",
      "invfreqcount",
      "freqrank",
      "invfreqrank",
      "invconjfreqrank",
      "freqranksquare",
      "invfreqranksquare",
      "invmodfreqrank",
      "invmodfreqrankmax0",
      "constant"
   ],
   "order-constant-weight": [ "0", "1" ],
   "split-clauses": [ "0", "4", "7" ],
   "simul-paramod": [None],
   "oriented-simul-paramod": [None],
   "split-reuse-defs": [None],
   "forward-context-sr": [None],
   "split-aggressive": [None],
   "define-heuristic": None,
   "definitional-cnf": [ None, "24" ],
   "prefer-initial-clauses": [None],
   "forward-demod-level": [ "0", "1", "2" ],
   "destructive-er": [None],
   "strong-destructive-er": [None],
   "destructive-er-aggressive": [None],
   "sine": None,
   "presat-simplify": [None],
   "condense": [None],
}

ignored = [
   "delete-bad-limit",
   "s",
   "tstp-in",
]

# Translation of E space to E options:
#
# sel                   <val>    => -W<val>, --literal-selection-strategy=<val>
# simparamod            none     => ""
#                       normal   => --simul-paramod 
#                       oriented => --oriented-simul-paramod
# srd                   0        => ""
#                       1        => --split-reuse-defs
# forwardcntxtsr        0        => ""
#                       1        => --forward-context-sr
# splaggr               0        => ""
#                       1        => --split-aggressive
# splcl                 0        => ""
#                       <val>    => --split-clauses=<val>
#           
# tord                  <val>    => -t<val>, --term-ordering=<val>
# tord_prec             <val>    => -G<val>, --order-precedence-generation=<val>
# tord_weight           <val>    => -w<val>, --order-weight-generation=<val>
# tord_const            0        => ""
#                       <val>    => -c<val>, --order-constant-weight=<val>
# sine$                 <vals>   => --sine='GSinE($G,$h,$gf,$D,$R,$L,$F)'
#                       0        => ""
#
# defcnf                1        => --definitional-cnf
# prefer                1        => --prefer-initial-clauses
# fwdemod               0,1      => --forward-demod-level=<val> 
#                       2        => ""
# der                   none     => ""
#                       std      => --destructive-er
#                       strong   => --destructive-er --strong-destructive-er
#                       agg      => --destructive-er --destructive-er-aggressive
#                       stragg   => --destructive-er --strong-destructive-er --destructive-er-aggressive
# presat                0        => ""
#                       1        => --presat-simplify
# condense              0        => ""
#                       1        => --condense
#



translation = {
   "literal-selection-strategy": "sel",
   "term-ordering": "tord",
   "order-precedence-generation": "tord_prec",
   "order-weight-generation": "tord_weight",
   "order-constant-weight": "tord_const",
   "split-clauses": "splcl",
   "simul-paramod": ("simparamod", "normal"),
   "oriented-simul-paramod": ("simparamod", "oriented"),
   "split-reuse-defs": ("srd", "1"),
   "forward-context-sr": ("forwardcntxtsr", "1"),
   "split-aggressive": ("splaggr", "1"),
   "define-heuristic": None,
   "definitional-cnf": ("defcnf", "1"),
   "prefer-initial-clauses": ("prefer", "1"),
   "forward-demod-level": "fwdemod",
   "destructive-er": None,
   "strong-destructive-er": None,
   "destructive-er-aggressive": None,
   "sine": None,
   "presat-simplify": ("presat", "1"),
   "condense": ("condense", "1"),

}

sines = [
   "sineG",
   "sineh",
   "sinegf",
   "sineD",
   "sineR",
   "sineL",
   "sineF", 
]

sinevals = {
   "sineG":  ["CountFormulas", "CountTerms"],
   "sineh":  ["", "hypos"],
   "sinegf": ["1.1","1.2","1.4","1.5","2.0","5.0","6.0"],
   "sineD":  ["","1","3","10","20","40","160"],
   "sineR":  ["","1","2","3","4","6"],
   "sineL":  ["10","20","40","60","80","100","200","500","20000"],
   "sineF":  ["1.0","0.8","0.6"],
}

# Translator limitations:
#
# * arguments can't contain "="
# * single character options must be written "-xValue" not "-x Value"
#

# TODO: 
# -F, --forward-demod-level
# --delete-bad-limit


def parse(proto):
   args = {}
   for x in proto:
      x = x.strip()
      if x.startswith("--"):
         x = x[2:]
         if "=" in x:
            (key,val) = x.split("=") 
         else:
            (key,val) = (x, None)
      elif x.startswith("-"):
         key = x[1]
         val = x[2:]
      if key in shotcuts:
         key = shotcuts[key]
      args[key] = val
   return args

def check(args):
   new = {}
   for (key,val) in args.items():
      if key in supported:
         if supported[key] and val not in supported[key]:
            sys.stderr.write("Warning: Unsupported value '%s' for key '%s'!\n" % (val,key))
         else:
            new[key] = val
      elif key not in ignored:
         sys.stderr.write("Warning: Unsupported option '%s'!\n" % key)
   return new

def givens(code):
   params = {}
   code = code.replace(" ","").strip("'\"")
   if code[0] == "(" and code[-1] == ")":
      code = code[1:-1]
   heurs = code.split("),")
   heurs = [x.split("*") for x in heurs]
   params["slots"] = len(heurs)
   for (n,(f,c)) in enumerate(heurs):
      params["freq%d"%n] = f
      params["cef%d"%n] = cef2block(c)
   return params

def sine(code):
   params = {}
   params["sine"] = "1"
   code = code.replace(" ","").strip("'")
   if not (code.startswith("GSinE(") and code.endswith(")")):
      sys.stderr.write("Warning: Invalid SinE value '%s'.\n" % code)
      return params
   code = code[6:-1]
   args = code.split(",")
   if len(args) != 7:
      sys.stderr.write("Warning: Invalid number of SinE arguments in '%s'.\n" % code)
      return params
   for (k, v) in zip(sines, args):
      if v.isdigit():
         v = "%s"%int(v) # ugly normalize: "02" to "2" etc.
      if v not in sinevals[k]:
         sys.stderr.write("Warning: Unsupported value for '%s' for sine argument '%s'.\n" % (v, k))
      params[k] = v if v else "none"
   return params

def der(args):
   if "strong-destructive-er" in args and "destructive-er-aggressive" in args:
      ret = "stragg"
   elif "destructive-er-aggressive" in args:
      ret = "agg"
   elif "strong-destructive-ar" in args:
      ret = "strong"
   elif "destructive-er" in args:
      ret = "std"
   else:
      ret = "none"
   return ret

def translate(args):
   params = dict(defaults)
   for (key,val) in args.items():
      trans = translation[key]
      if isinstance(trans, str):
         params[trans] = val
      elif key == "define-heuristic":
         params.update(givens(val))
      elif key == "sine":
         params.update(sine(val))
      elif trans is None:
         continue # "der" stuff handled below
      else:
         params[trans[0]] = trans[1]
   params["der"] = der(args)
   return params

if len(sys.argv) != 2:
   sys.stderr.write("usage %s: protocol-file\n" % sys.argv[0])
   sys.exit(-1)

proto = open(sys.argv[1]).read().strip().split()
args = parse(proto)
args = check(args)
params = translate(args)

runner = EproverRunner()
print(runner.repr(params))

