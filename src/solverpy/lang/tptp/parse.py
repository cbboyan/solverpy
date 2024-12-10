import antlr4 as ant

from .TptpLexer import TptpLexer
from .TptpParser import TptpParser
from .TptpSetVisitor import TptpSetVisitor

def is_clause(fml):
   return (type(fml) == tuple) and (len(fml) == 2) and \
          (type(fml[0]) == type(fml[1]) == frozenset)

def is_equality(term):
   return (type(term) == tuple) and (len(term) == 2) and \
          (term[0] == "=") and (type(term[1]) == frozenset)

def split4(cls):
   #assert is_clause(cls)
   (pos, neg) = cls
   pos_eq = [x for x in pos if is_equality(x)]
   neg_eq = [x for x in neg if is_equality(x)]
   pos_non = [x for x in pos if not is_equality(x)]
   neg_non = [x for x in neg if not is_equality(x)]
   return (pos_eq, neg_eq, pos_non, neg_non)

def stream(s, callParse):
   lexer = TptpLexer(s)
   token_stream = ant.CommonTokenStream(lexer)
   parser = TptpParser(token_stream)
   tree = callParse(parser)
   visitor = TptpSetVisitor()
   return visitor.visit(tree)

def problem(f_in):
   "Parse a TPTP file."
   s = ant.FileStream(f_in)
   ret = stream(s, lambda p: p.tptp_file())
   assert ret[-1] == "<EOF>"
   ret.pop()
   return ret

def formula(fml):
   "Parse TPTP formula from string, eg: `cnf(a, axiom, (~p)).`"
   s = ant.InputStream(fml)
   return stream(s, lambda p: p.annotated_formula())

def parents(infer):
   "Extract list of parents from an inference info."
   ret = []
   def follow(node):
      if type(node) == str:
         ret.append(node)
      else:
         ret.extend(parents(node))
   match infer:
      case ("file", (fname, axiom)):
         ret.append(("file", (fname, axiom)))
      case ("file", src):
         ret.append(("file", src))
      case ("proof", src):
         follow(src)
      case ("infer", srcs):
         for (_,src) in srcs:
            follow(src)
      case (info, node) if type(info)==type(node)==str:
         ret.append(node)
      case _:
         raise Exception(f"Unsupported inference: {infer}")
   return ret

