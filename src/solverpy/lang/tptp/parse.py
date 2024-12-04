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
   ret.pop() # "<EOF>" string at the and
   return ret

def formula(fml):
   "Parse TPTP formula from string, eg: `cnf(a, axiom, (~p)).`"
   s = ant.InputStream(fml)
   return stream(s, lambda p: p.annotated_formula())

