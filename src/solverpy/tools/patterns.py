import re

def single(pattern, output, default):
   mo = re.search(pattern, output)
   return mo.group(1) if mo else default
   
def keyval(pattern, output, table=None) -> dict[str, str]:
   res = dict(re.findall(pattern, output))
   if table:
      res = {table[x]:res[x] for x in table if x in res}
   return res

def valkey(pattern, output, table=None):
   res = {k:v for (v,k) in re.findall(pattern, output)}
   if table:
      res = {table[x]:res[x] for x in table if x in res}
   return res

def mapval(data, apply):
   return {x:apply(y) for (x,y) in data.items()}

