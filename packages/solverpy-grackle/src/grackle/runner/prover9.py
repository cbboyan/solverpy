import re
import tempfile
import os 
from os import path, getenv
from .runner import GrackleRunner
#from grackle.trainer.prover9.domain import DEFAULTS
from grackle.trainer.prover9.default import DefaultDomain

P_BINARY = "prover9"
P_STATIC = "-f "     # is Prover9's flag for input files (strategies and problems)
P_LIMIT = " -t %ss"  # is Prover9's flag for time limit

# Prover9 has two possible states for End of Search: 
P_OK = ['THEOREM PROVED']
P_FAILED = ['SEARCH FAILED']
P_RESULTS = P_OK + P_FAILED

TIMEOUT = "timeout --kill-after=1 --foreground %s " # note the space at the end

KEYS = [
   #"SZS status",
   "User_CPU=",
   #"Active clauses:",
   #"Termination reason:",
]

PAT = re.compile(r"^%% (%s) (\S*)" % "|".join(KEYS), flags=re.MULTILINE)
pattern_wall_clock = r'User_CPU=(\d+\.\d+)' # We can take User_CPU, System_CPU, Wall_clock
pattern_kept = r'Kept=(\d+)'                # kept Clauses

INTS=frozenset("""
weight
literals
variables
depth
level
""".strip().split("\n"))

IGNORED = [
   "Fatal error:  renum_vars_recurse: too many variables",
   "Fatal error:  sread_term error",
   "Fatal error:  sos_displace2, cannot find worst clause",
   "Fatal error:  Circular relational definitions",
]
      
HEADER = """
assign(max_megs, 2048).
clear(print_given).
"""

# update this whenever prover9.actions.ActionsDomain / GivenDomain change the default
DEF_FLAG = dict(counter="none", cond=100, action="set", flag="reuse_denials")
DEF_CHANGE = dict(counter="none", cond=100, action="max_given", value=0)
DEF_COND = dict(cond="positive", neg="yes", val=1, connect="and")
DEF_PART = dict(ratio=0, order="weight")

def make_action_flag(cur, selector=None):
   cur = DEF_FLAG | cur
   return "   %(counter)s=%(cond)s -> %(action)s(%(flag)s).\n" % cur

def make_action_change(cur, selector=None):
   cur = DEF_CHANGE | cur
   return "   %(counter)s=%(cond)s -> assign(%(action)s, %(value)s).\n" % cur

def make_cond(cur, selector=None):
   cur = DEF_COND | cur
   cont = "" if "connect" not in cur else (" & " if cur['connect'] == "and" else " | ")
   if "cond" not in cur:
      return ""
   if cur['cond'] in INTS:
      sign = "<" if cur['neg'] == "no" else ">="
      return f"{cur['cond']}{sign}{cur['val']}{cont}"
   else:
      sign = "" if cur['neg'] == "no" else "-"
      return f"{sign}{cur['cond']}{cont}"

def make_keepdel_cond(cur, selector=None):
   DEF_COND["cond"] = "none"
   prop = make_lines(cur, "prp", make_cond, "cond", "none").rstrip(" |&")
   return f"   {prop}.\n"

def make_given_low(cur, selector=None):
   cur = DEF_PART | cur
   DEF_COND["cond"] = "positive"
   prop = make_lines(cur, "prp", make_cond, "cond", "none").rstrip(" |&")
   return f"   part({selector}, low, {cur['order']}, {prop}) = {cur['ratio']}.\n"

def make_given_high(cur, selector=None):
   cur = DEF_PART | cur
   DEF_COND["cond"] = "positive"
   prop = make_lines(cur, "prp", make_cond, "cond", "none").rstrip(" |&")
   return f"   part({selector}, high, {cur['order']}, {prop}) = {cur['ratio']}.\n"

def make_lines(params, selector, builder, master="counter", deactive="none"):
   def move(val=None):
      nonlocal n, key, cur
      n = val if val is not None else (n+1)
      key = f"{n}_{master}"
      cur = {x[2:]:y for (x,y) in params.items() if  x.startswith(str(n))}

   lines = ""
   params = {x[len(selector):]:y for (x,y) in params.items() if x.startswith(f"{selector}")}
   n = None
   key = None
   cur = None
   move(0)
   while key in params and str(params[key]) != deactive:
      lines += builder(cur, selector+key[0])
      move()
   return lines

def make_actions(params):
   lines = ""
   lines += make_lines(params, "flg", make_action_flag, "counter", "none")
   lines += make_lines(params, "cng", make_action_change, "counter", "none")
   return f"\nlist(actions).\n{lines}end_of_list.\n" if lines.strip() else ""

def make_given(params):
   lines = ""
   lines += make_lines(params, "hgh", make_given_high, "ratio", "0")
   lines += make_lines(params, "low", make_given_low, "ratio", "0")
   nonempty = lines.strip() != ""
   if nonempty:
      lines += "   part(default, low, age, all) = 1.\n" 
   return f"\nlist(given_selection).\n{lines}end_of_list.\n" if nonempty else ""

def make_keepdel(params):
   keps = make_lines(params, "kep", make_keepdel_cond, "prp0_cond", "none")
   dels = make_lines(params, "del", make_keepdel_cond, "prp0_cond", "none")
   lines = ""
   lines += f"\nlist(keep).\n{keps}end_of_list.\n" if keps.strip() else ""
   lines += f"\nlist(delete).\n{dels}end_of_list.\n" if dels.strip() else ""
   return lines

def make_strategy(params, defaults):
   #for x in defaults:
   #   if x.startswith("a__") and x not in params:
   #      params[x] = defaults[x]
   params = {x[3:]:y for (x,y) in params.items() if x.startswith(f"a__")}
   return make_actions(params) + make_given(params) + make_keepdel(params)

class Prover9Runner(GrackleRunner):

   def __init__(self, config={}):
      GrackleRunner.__init__(self, config)
      self.default("penalty", 100000000)
      penalty = self.config["penalty"]
      self.default("penalty.error", penalty*1000)
      self.default_domain(DefaultDomain)
      #self.conds = self.conditions(CONDITIONS)
      self.temp_file_to_delete = ''  # for the temp files


   def args(self, params):
      lines = []
      a_set = []
      a_clear = []
      a_assign = []
      for (key, val) in params.items():
         if key == "max_megs" or key.startswith("a__"): # advanced features
            continue
         if val == "set": 
            a_set.append(key)
         elif val == "clear":
            a_clear.append(key)
         else:
            a_assign.append((key, val))
      lines.extend([f"clear({key})." for key in sorted(a_clear)])
      if a_clear: lines.append("")
      lines.extend([f"set({key})." for key in sorted(a_set)])
      if a_set: lines.append("")
      lines.extend([f"assign({key}, {val})." for (key,val) in sorted(a_assign)])
      if a_assign: lines.append("")
      lines.append(make_strategy(params, self.domain.defaults))
      header = "\n".join(lines)
      if not header.strip():
         # empty strategy
         header = "set(auto).\n"
      header += HEADER
      return header

   # Create a temporary strategy file in memory
   # Explanation: Prover9 doesn' take strategies like Vampire directly, 
   # Prover9 needs an input file with strategies, so we create one. 
   def create_temp_strategy_file(self, params):
      with tempfile.NamedTemporaryFile(mode='w+', delete=False, prefix="prover9-strat-") as f_tmp:
         f_tmp.write(self.args(params))
      return f_tmp.name

   def cmd(self, params, inst):
      params = self.clean(params)
      temp_strategy_file = self.create_temp_strategy_file(params)
      self.temp_file_to_delete = temp_strategy_file
      problem = path.join(getenv("SOLVERPY_BENCHMARKS", "."), inst)
      vlimit = P_LIMIT % self.config["timeout"] if "timeout" in self.config else ""
      timeout = TIMEOUT % (self.config["timeout"]+1) if "timeout" in self.config else ""

      cmdargs = f"{timeout} {P_BINARY} {vlimit} {P_STATIC} {temp_strategy_file} {problem}"
      return cmdargs

   def process(self, out, inst):
      out = out.decode()
 
      if "THEOREM PROVED" in out:
        result = "THEOREM PROVED"
      else:
         if ("SEARCH FAILED" not in out) and ("Fatal error" in out):
            for ignored in IGNORED:
               if ignored in out:
                  return [self.config["penalty.error"], self.config["timeout"], "IGNORED", -1]
            return None # report error
         result = "SEARCH FAILED"  
      ok = self.success(result)

      # Search for the pattern in the output
      match_time = re.search(pattern_wall_clock, out)
      runtime = 0.0
      # If a match is found, extract the Wall_clock value
      if match_time:
         runtime = float(match_time.group(1))
      # set to default 0.001 if the Wall_clock is null       
      else:
         runtime = 0.0001

      quality = 10+int(1000*runtime) if ok else self.config["penalty"]   

      match_resources = re.search(pattern_kept, out)
      if match_resources:
         resources = int(match_resources.group(1))
      else:
         resources = 99999999

      if self.temp_file_to_delete:
         os.unlink(self.temp_file_to_delete)  # Deleting temp File

      return [quality, runtime, result, resources]
     

   def success(self, result):
      return result in P_OK

   def clean(self, params):
      params = {x:params[x] for x in params if params[x] != self.domain.defaults[x]}
      return params

