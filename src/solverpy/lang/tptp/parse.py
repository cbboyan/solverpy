import antlr4 as ant

from .TptpLexer import TptpLexer
from .TptpParser import TptpParser
from .TptpSetVisitor import TptpSetVisitor

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
   (label, links) = infer
   if type(links) == str:
      ret.append(links)
   elif label == "file":
      ret.append(f"<file {links}>")
   elif label == "proof":
      if type(links) == str:
         ret.append(links)
      else:
         ret.extend(parents(links))
   elif label == "infer":
      for (_,inf0) in links:
         if type(inf0) == str:
            ret.append(inf0)
         else:
            ret.extend(parents(inf0))
   else:
      raise Exception(f"Unsupported inference: {infer}")
   return ret

