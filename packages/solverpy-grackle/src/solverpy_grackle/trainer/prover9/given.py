from ..domain.custom import CustomDomain

class GivenDomain(CustomDomain):
   
   def __init__(self, low=2, high=2, conds=2, **kwargs):
      kwargs = dict(kwargs, low=low, high=high, conds=conds)
      self.n_low = low
      self.n_high = high
      self.n_conds = conds
      CustomDomain.__init__(self, **kwargs)
      self.init()

   def init(self):
      self.add_parts("low", self.n_low)
      self.add_parts("hgh", self.n_high)
   
   def split(self, params):
      cond = lambda x: x.startswith("a__low") or x.startswith("a__hgh")
      fixed = {x:y for (x,y) in params.items() if not cond(x)}
      params = {x:y for (x,y) in params.items() if cond(x)}
      return (params, fixed)

   def add_param(self, name, domain, default=None, acc=None):
      super().add_param(name, domain, default)
      if acc is not None: acc.append(name)

   def add_part(self, name): 
      acc = []
      self.add_param(f"{name}_ratio", RATIO)
      self.add_param(f"{name}_order", ORDER, acc=acc)
      for n in range(self.n_conds):
         dom = (["none"] if n>0 else [])+BASIC+INTS
         acc0 = []
         self.add_param(f"{name}_prp{n}_cond", dom, acc=acc)
         self.add_param(f"{name}_prp{n}_neg", YESNO, acc=acc0)
         self.add_param(f"{name}_prp{n}_val", VALUES, acc=acc)
         self.add_dep(f"{name}_prp{n}_val", f"{name}_prp{n}_cond", INTS)
         if n != self.n_conds - 1:
            self.add_param(f"{name}_prp{n}_connect", ANDOR, acc=acc0)
            self.add_dep(f"{name}_prp{n}_connect", f"{name}_prp{n+1}_cond", BASIC+INTS)
         if n > 0:
            for x in acc0:
               self.add_dep(x, f"{name}_prp{n}_cond", BASIC+INTS)
         acc.extend(acc0)
      for x in acc:
         self.add_dep(x, f"{name}_ratio", ACTIVE)

   def add_parts(self, typ, count):
      for n in range(count):
         self.add_part(f"a__{typ}{n}")
         for m in range(n):
            self.add_dep(f"a__{typ}{n}_ratio", f"a__{typ}{m}_ratio", ACTIVE)
      if count:
         for x in INACTIVE:
            self.add_dep(x, f"a__{typ}0_ratio", [0])
 
BASIC="""
positive
negative
mixed
unit
horn
definite
has_equality
true
false
initial
resolvent
hyper_resolvent
ur_resolvent
factor
paramodulant
back_demodulant
subsumer
""".strip().split("\n")
# all

INTS="""
weight
literals
variables
depth
level
""".strip().split("\n")

RATIO=[0,1,2,3,4,5,10,20,50,200]
VALUES=[1,2,3,5,7,10,15,20,50,100,500,1000]
ACTIVE=[x for x in RATIO if x != 0]

ORDER=["weight", "age", "random"]
YESNO=["yes", "no"]
ANDOR=["and", "or"]

INACTIVE=frozenset(
  "age_part,true_part,false_part,weight_part,random_part".split(",")
)

