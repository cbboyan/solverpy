if __name__ is not None and "." in __name__:
    from .TptpVisitor import TptpVisitor
    from .TptpParser import TptpParser
else:
    from TptpVisitor import TptpVisitor
    from TptpParser import TptpParser
      
def flatten(lst):
   if type(lst) == str:
      yield lst
   else:
      for member in lst:
         for sub in flatten(member):
            yield sub

class TptpSetVisitor(TptpVisitor):

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self._subst = {}

   def visitCnf_literal(self, ctx:TptpParser.Cnf_literalContext):
      """
      cnf_literal             : fof_atomic_formula | Not fof_atomic_formula
                              | fof_infix_unary;
      """
      if ctx.getChildCount() == 2:
         # negated atom
         return ("~", self.visit(ctx.getChild(1)))
      ret = self.defaultVisit(ctx)
      if (len(ret) == 3) and (ret[1] in ["=", "!="]):
         # equality and inequality
         return (ret[1], frozenset([ret[0], ret[2]]))
      return ret
    
   def visitCnf_disjunction(self, ctx:TptpParser.Cnf_disjunctionContext):
      """
      cnf_disjunction         : cnf_literal | cnf_disjunction Or cnf_literal;
      """
      if ctx.getChildCount() == 1:
         # single literal
         return frozenset([self.visit(ctx.getChild(0))])
      # multi-literal
      disjunction = self.visit(ctx.getChild(0))
      literal = self.visit(ctx.getChild(2))
      if type(literal) != frozenset:
         literal = frozenset([literal])
      return disjunction | literal
    
   def visitAnnotated_formula(self, ctx:TptpParser.Annotated_formulaContext):
      self._subst.clear()
      return super().visitAnnotated_formula(ctx)
    
   def visitCnf_formula(self, ctx:TptpParser.Cnf_formulaContext):
      """
      cnf_formula             : cnf_disjunction | '(' cnf_disjunction ')';
      """
      if ctx.getChildCount() == 1:
         return self.visit(ctx.getChild(0))
      else:
         return self.visit(ctx.getChild(1))
    
   def visitVariable(self, ctx:TptpParser.VariableContext):
      """
      variable                : Upper_word;
      """
      var = ctx.getText()
      if var not in self._subst:
         self._subst[var] = len(self._subst)
      return f"V{self._subst[var]:d}"
    
   def visitAnnotations(self, ctx:TptpParser.AnnotationsContext):
      """
      annotations             : ',' source optional_info?;
      """
      return self.visit(ctx.getChild(1))

   def visitInference_record(self, ctx:TptpParser.Inference_recordContext):
      """
      inference_record        : 'inference(' inference_rule ',' useful_info ',' inference_parents ')';
      """
      ret = self.visit(ctx.getChild(5))
      return tuple(x for x in flatten(ret))

del TptpVisitor
del TptpParser

