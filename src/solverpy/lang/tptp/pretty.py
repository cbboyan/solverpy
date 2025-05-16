from .parse import is_clause, split4

def term(t, sgn=True):
   snot = "" if sgn else "~"
   match t:
      case ("=", sides):
         sides = sorted(term(x) for x in sides)
         lhs = sides[0]   
         rhs = sides[1] if len(sides)>1 else lhs
         op = "=" if sgn else "!="
         return f"{lhs}{op}{rhs}"
      case args if type(t) == tuple:
         args = " ".join(term(x) for x in args)
         return f"{snot}({args})"
      case args if type(t) == list:
         args = " ".join(term(x) for x in args)
         return f"{snot}[{args}]"
      case _:
         assert type(t) == str
         return f"{snot}{t}"

def literals(lits, sgn):
   return " | ".join(sorted(term(t,sgn) for t in lits))

def clause(cls):
   (pe, ne, pn, nn) = split4(cls)
   pe = literals(pe, True)
   ne = literals(ne, False)
   pn = literals(pn, True)
   nn = literals(nn, False)
   return " | ".join(x for x in [pe, ne, pn, nn] if x)

def formula(fml):
   if is_clause(fml):
      return clause(fml)
   return " ".join(term(x) for x in fml)

def inference(inf):
   return term(inf)

def annotated(lang, name, role, fml, inf=None):
   if inf:
      pref = f"{lang}/{role[:3]}/{name} <{inference(inf)}>"
      return f"{pref:50s}\t{formula(fml)}"
   else:
      return f"{lang}/{role[:3]}/{name}\t{formula(fml)}"

