from ..domain.custom import CustomDomain
from .given import BASIC, INTS, YESNO, ANDOR, VALUES

class KeepDeleteDomain(CustomDomain):
   
   def __init__(self, keep=2, delete=2, conds=2, **kwargs):
      kwargs = dict(kwargs, keep=keep, delete=delete, conds=conds)
      self.n_keep = keep
      self.n_delete = delete
      self.n_conds = conds
      CustomDomain.__init__(self, **kwargs)
      self.init()

   def init(self):
      self.add_conditions("kep", self.n_keep)
      self.add_conditions("del", self.n_delete)
   
   def split(self, params):
      cond = lambda x: x.startswith("a__kep") or x.startswith("a__del")
      fixed = {x:y for (x,y) in params.items() if not cond(x)}
      params = {x:y for (x,y) in params.items() if cond(x)}
      return (params, fixed)

   def add_param(self, name, domain, default=None, acc=None):
      super().add_param(name, domain, default)
      if acc is not None: acc.append(name)
   
   def add_conditions(self, typ, count):
      for n in range(count):
         name = f"a__{typ}{n}"
         self.add_cond(name)
         for m in range(n):
            self.add_dep(f"a__{typ}{n}_prp0_cond", f"a__{typ}{m}_prp0_cond", BASIC+INTS)

   def add_cond(self, name):
      for n in range(self.n_conds):
         acc0 = []
         self.add_param(f"{name}_prp{n}_cond", ["none"]+BASIC+INTS)
         self.add_param(f"{name}_prp{n}_neg", YESNO, acc=acc0)
         self.add_param(f"{name}_prp{n}_val", VALUES)
         self.add_dep(f"{name}_prp{n}_val", f"{name}_prp{n}_cond", INTS)
         if n != self.n_conds - 1:
            self.add_param(f"{name}_prp{n}_connect", ANDOR, acc=acc0)
            self.add_dep(f"{name}_prp{n}_connect", f"{name}_prp{n+1}_cond", BASIC+INTS)
         for x in acc0:
            self.add_dep(x, f"{name}_prp{n}_cond", BASIC+INTS)
      # all the options depend on the master option to be active (not "none")
      master = f"{name}_prp0_cond"
      for n in range(1, self.n_conds):
         self.add_dep(f"{name}_prp{n}_cond", master, BASIC+INTS)

