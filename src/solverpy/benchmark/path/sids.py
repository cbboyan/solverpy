import os
import re

DEFAULT_NAME = "strats"
DEFAULT_DIR = os.getenv("SOLVERPY_STRATS", DEFAULT_NAME)

ARGUMENT = re.compile(r"@@@\s*([^@: ]*)\s*:\s*([^@: ]*)\s*@@@")

def path(sid):
   f_sid = sid.split("@")[0] if ("@" in sid) else sid
   return os.path.join(DEFAULT_DIR, f_sid)

def load(sid):
   return open(path(sid)).read().strip()

def save(sid, strategy):
   f_sid = path(sid, realfile=False)
   os.makedirs(os.path.dirname(f_sid), exist_ok=True)
   open(f_sid, "w").write(strategy.strip())

def unspace(strategy):
   return " ".join(x for x in strategy.split() if x)

def split(sid):
   args = {}
   if "@" in sid:
      (sid, args) = sid.split("@")
      args = args.split(":")
      args = [x.split("=") for x in args]      
      args = {x.strip():y.strip() for (x,y) in args}
   return (sid, args)

def instatiate(strategy, args):
   args0 = defaults(strategy)
   args0.update(args)
   ret = ARGUMENT.sub(lambda mo: args0[mo.group(1)], strategy)
   return ret

def defaults(strategy):
   ret = ARGUMENT.findall(strategy)
   ret = {x.strip():y.strip() for (x,y) in ret}
   return ret

def normalize(sid):
   strategy = load(sid)
   defs = defaults(strategy)
   (sid, args) = split(sid)
   args = {x:y for (x,y) in args.items() if y != defs[x]}
   args = ":".join(f"{x}={args[x]}" for x in sorted(args))
   return "%s@%s" % (sid, args)
   
