if __name__ is not None and "." in __name__:
    from .TptpDefaultVisitor import TptpDefaultVisitor
    from .TptpParser import TptpParser
else:
    from TptpDefaultVisitor import TptpDefaultVisitor
    from TptpParser import TptpParser

IGNORED = "[(,)]"

class TptpVisitor(TptpDefaultVisitor):

   def defaultVisit(self, ctx):
      def childVisit(ch):
         ret0 = self.visit(ch)
         if ret0 is None:
            ret0 = ch.getText()
            if ret0 in IGNORED: 
               ret0 = None
         return ret0
      #name = f"{ctx.__class__.__name__[:-7]}({ctx.getChildCount()})"
      
      if ctx.start == ctx.stop:
         # terminal
         ret = self.visit(ctx.getChild(0))
         if ret is None:
            ret = ctx.getChild(0).getText()
      elif ctx.getChildCount() == 1:
         # single child nonterminal
         ret = self.visit(ctx.getChild(0))
      else:
         # multiple children nonterminal
         ret = [childVisit(ch) for ch in ctx.children]
         ret = [x for x in ret if x is not None]
      return ret 
  
   def visitChild(self, ctx, i):
      return self.visit(ctx.getChild(i))

   def visitChildrenEven(self, ctx):
      cnt = ctx.getChildCount()
      return [self.visitChild(ctx,i) for i in range(0,cnt,2)]

   def visitChildrenOdd(self, ctx):
      cnt = ctx.getChildCount()
      return [self.visitChild(ctx,i) for i in range(1,cnt,2)]

   def visitFof_plain_term(self, ctx:TptpParser.Fof_plain_termContext):
      """
      fof_plain_term           : constant
                               | functor '(' fof_arguments ')';
      """
      head = self.visit(ctx.getChild(0))
      if ctx.getChildCount() == 1:
         return head
      body = self.visit(ctx.getChild(2))
      return (head,) + body
    
   def visitFof_arguments(self, ctx:TptpParser.Fof_argumentsContext):
      """
      fof_arguments           : fof_term (',' fof_term)*;
      """
      return tuple(self.visitChildrenEven(ctx))
   
   def visitAnnotated_formula(self, ctx:TptpParser.Annotated_formulaContext):
      "Strips `(` from `cnf(` or `fof(`, etc. and removes postfix `).`"
      ret = self.defaultVisit(ctx)
      ret[0] = ret[0].rstrip("(")
      ret.pop()
      return tuple(ret)

del TptpDefaultVisitor
del TptpParser

