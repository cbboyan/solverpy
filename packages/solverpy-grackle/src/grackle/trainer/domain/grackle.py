
def _parse_params(raw):
   """Parse raw PCS PARAMS string into {name: [values]} dict."""
   params = {}
   for line in raw.strip().splitlines():
      line = line.strip()
      if not line or line.startswith("#"):
         continue
      name = line.split()[0]
      vals_str = line[line.index("{") + 1 : line.index("}")]
      params[name] = vals_str.split(",")
   return params


def _parse_conditions(raw):
   """Parse raw PCS CONDITIONS string into list of (slave, master, values) tuples."""
   conds = []
   for line in raw.strip().splitlines():
      line = line.strip()
      if not line or "|" not in line or line.startswith("#"):
         continue
      slave, rest = line.split("|", 1)
      master, vals = rest.strip().split(" in ", 1)
      slave = slave.strip()
      master = master.strip()
      vals = [v.strip() for v in vals.strip().strip("{}").split(",")]
      conds.append((slave, master, vals))
   return conds


def _parse_forbiddens(raw):
   """Parse raw PCS FORBIDDENS string into list of {param=val,...} strings."""
   return [
      line.strip()
      for line in raw.strip().splitlines()
      if line.strip() and not line.strip().startswith("#")
   ]


def dotjoin(lst):
   if isinstance(lst, str):
      lst = lst.strip()
      if lst.startswith("{") and lst.endswith("}"):
         return lst
      return "{%s}" % lst 
   return "{%s}" % ",".join(str(x) for x in lst)

class GrackleDomain:
   
   def __init__(self, **kwargs):
      self._kwargs = dict(kwargs)
   
   def __repr__(self):
      args = [f"{x}={y}" for (x,y) in self._kwargs.items()]
      return f"{type(self).__name__}({','.join(args)})"
    
   @property
   def name(self):
      return f"{type(self).__name__}"
   
   @property
   def params(self):
      return {}

   @property
   def defaults(self):
      return {}

   @property 
   def conditions(self):
      return []

   @property
   def forbiddens(self):
      return []

   def join(self, params, fixed):
      return params | fixed

   def split(self, params):
      mine  = {k: v for k, v in params.items() if k in self.params}
      other = {k: v for k, v in params.items() if k not in self.params}
      return (mine, other)

   def dump_param(self, key, defaults=None):
      def default(key):
         return defaults[key] if (defaults and (key in defaults)) else self.defaults[key]
      dom = dotjoin(self.params[key])
      return f"{key} {dom} [{default(key)}]"

   def dump_condition(self, cond):
     if not isinstance(cond, str):
        (slave, master, values) = cond
        values = dotjoin(values)
        cond = f"{slave} | {master} in {values}"
     return cond

   def dump_forbidden(self, forbidden):
     return dotjoin(forbidden)

   def dump(self, defaults=None):
      lines = []
      # parameter domain (","-separated string or list of values)
      for key in sorted(self.params):
         lines.append(self.dump_param(key, defaults=defaults))
      lines.append("")
      # conditions (either string or 3-tuples)
      for cond in self.conditions:
         if not cond:
            continue
         lines.append(self.dump_condition(cond))
      lines.append("")
      # forbiddens (strings or string-lists)
      for f in self.forbiddens:
         lines.append(self.dump_forbidden(f))
      return "\n".join(lines)

