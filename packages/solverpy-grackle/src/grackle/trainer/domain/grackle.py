from typing import Any

Condition = tuple[str, str, list[str]]
"""A parameter condition: (slave, master, allowed_values)."""


def _parse_params(raw: str) -> dict[str, list[str]]:
   """Parse raw PCS PARAMS string into {name: [values]} dict."""
   params: dict[str, list[str]] = {}
   for line in raw.strip().splitlines():
      line = line.strip()
      if not line or line.startswith("#"):
         continue
      name = line.split()[0]
      vals_str = line[line.index("{") + 1 : line.index("}")]
      params[name] = vals_str.split(",")
   return params


def _parse_conditions(raw: str) -> list[Condition]:
   """Parse raw PCS CONDITIONS string into list of (slave, master, values) tuples."""
   conds: list[Condition] = []
   for line in raw.strip().splitlines():
      line = line.strip()
      if not line or "|" not in line or line.startswith("#"):
         continue
      slave, rest = line.split("|", 1)
      master, vals = rest.strip().split(" in ", 1)
      slave = slave.strip()
      master = master.strip()
      vals_list = [v.strip() for v in vals.strip().strip("{}").split(",")]
      conds.append((slave, master, vals_list))
   return conds


def _parse_forbiddens(raw: str) -> list[str]:
   """Parse raw PCS FORBIDDENS string into list of {param=val,...} strings."""
   return [
      line.strip()
      for line in raw.strip().splitlines()
      if line.strip() and not line.strip().startswith("#")
   ]


def dotjoin(lst: str | list[Any]) -> str:
   if isinstance(lst, str):
      lst = lst.strip()
      if lst.startswith("{") and lst.endswith("}"):
         return lst
      return "{%s}" % lst
   return "{%s}" % ",".join(str(x) for x in lst)


class GrackleDomain:

   def __init__(self, **kwargs: Any):
      self._kwargs = dict(kwargs)

   def __repr__(self) -> str:
      args = [f"{x}={y}" for (x,y) in self._kwargs.items()]
      return f"{type(self).__name__}({','.join(args)})"

   @property
   def name(self) -> str:
      return f"{type(self).__name__}"

   @property
   def params(self) -> dict[str, list[str]]:
      return {}

   @property
   def defaults(self) -> dict[str, str]:
      return {}

   @property
   def conditions(self) -> list[Condition]:
      return []

   @property
   def forbiddens(self) -> list[str]:
      return []

   def join(self, params: dict[str, str], fixed: dict[str, str]) -> dict[str, str]:
      return params | fixed

   def split(self, params: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
      mine  = {k: v for k, v in params.items() if k in self.params}
      other = {k: v for k, v in params.items() if k not in self.params}
      return (mine, other)

   def dump_param(self, key: str, defaults: dict[str, str] | None = None) -> str:
      def default(key: str) -> str:
         return defaults[key] if (defaults and (key in defaults)) else self.defaults[key]
      dom = dotjoin(self.params[key])
      return f"{key} {dom} [{default(key)}]"

   def dump_condition(self, cond: Condition | str) -> str:
      if not isinstance(cond, str):
         (slave, master, values) = cond
         values_str = dotjoin(values)
         cond = f"{slave} | {master} in {values_str}"
      return cond

   def dump_forbidden(self, forbidden: str | list[Any]) -> str:
      return dotjoin(forbidden)

   def dump(self, defaults: dict[str, str] | None = None) -> str:
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
