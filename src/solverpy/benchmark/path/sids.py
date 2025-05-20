import os
import re

from . import bids

NAME = "strats"

ARGUMENT = re.compile(r"@@@\s*([^@: ]*)\s*:\s*([^@: ]*)\s*@@@")

def path(sid: str) -> str:
   f_sid = sid.split("@")[0] if ("@" in sid) else sid
   return os.path.join(bids.dbpath(NAME), f_sid)

def load(sid: str) -> str:
   return open(path(sid)).read().strip()

def save(sid: str, strategy: str) -> None:
   f_sid = path(sid)
   os.makedirs(os.path.dirname(f_sid), exist_ok=True)
   open(f_sid, "w").write(strategy.strip())

def name(sid: str) -> str:
   return sid.replace("/", "--")

def unspace(strategy: str) -> str:
   return " ".join(x for x in strategy.split() if x)

def split(sid: str) -> tuple[str, dict[str, str]]:
   args = {}
   if "@" in sid:
      (sid, args) = sid.split("@")
      args = args.split(":")
      args = [x.split("=") for x in args]      
      args = {x.strip():y.strip() for (x,y) in args}
   return (sid, args)

def instatiate(strategy: str, args: dict[str, str]) -> str:
   args0 = defaults(strategy)
   args0.update(args)
   ret = ARGUMENT.sub(lambda mo: args0[mo.group(1)], strategy)
   return ret

def defaults(strategy: str) -> dict[str, str]:
   ret = ARGUMENT.findall(strategy)
   ret = {x.strip():y.strip() for (x,y) in ret}
   return ret

def fmt(base: str, args: dict[str, str]) -> str:
   args0 = ":".join(f"{x}={args[x]}" for x in sorted(args))
   return f"{base}@{args0}"

def normalize(sid: str) -> str:
   strategy = load(sid)
   defs = defaults(strategy)
   (sid, args) = split(sid)
   args = {x:y for (x,y) in args.items() if y != defs[x]}
   return fmt(sid, args)
   
