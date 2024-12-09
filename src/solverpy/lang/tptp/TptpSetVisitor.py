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
         yield from flatten(member)

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
      return (ret,) if type(ret)==str else ret
    
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

      source                  : dag_source | ...
      dag_source              : name | inference_record;
      """
      source = self.visit(ctx.getChild(1))
      if ctx.getChildCount() > 2:
         opt = self.visit(ctx.getChild(2))
         if type(opt) == str:
            return (opt, source)
         return (source, opt)

      return source

   def visitOptional_info(self, ctx:TptpParser.Optional_infoContext):
      """
      optional_info           : ',' useful_info;
      """
      return self.visit(ctx.getChild(1))
    
   def visitUseful_info(self, ctx:TptpParser.Useful_infoContext):
      """
      useful_info             : '[]' | '[' info_items ']' | general_list;
      
      info_items              : info_item ( ',' info_item )*; // #INFO flattened
      """
      if ctx.getChildCount() == 3:
         ret = self.visit(ctx.getChild(1))
      else:
         ret = self.defaultVisit(ctx)
      if type(ret)==list and len(ret)==1 and type(ret[0])==str:
         ret = ret[0].strip("'\"")
      else:
         print(f"Warning: Possibly unsupported useful_info: {ret}")
      return ret

   def visitInference_record(self, ctx:TptpParser.Inference_recordContext):
      """
      inference_record        : 'inference(' inference_rule ',' useful_info ',' inference_parents ')';
      """
      rule = self.visit(ctx.getChild(1))
      parents = self.visit(ctx.getChild(5))
      return ("infer", tuple((rule,x) for x in parents))
    
   def visitInference_parents(self, ctx:TptpParser.Inference_parentsContext):
      """
      inference_parents       : '[]' | '[' parent_list ']';
      """
      if ctx.getChildCount()==1:
         return []
      ret = self.visit(ctx.getChild(1))
      return ret
   
   # Visit a parse tree produced by TptpParser#parent_list.
   def visitParent_list(self, ctx:TptpParser.Parent_listContext):
      """
      parent_list             : parent_info ( ',' parent_info )*; // #INFO flattened

      parent_info             : source parent_details?; // #INFO ? because parent_details may be empty
      """
      ret = self.visitChildrenEven(ctx)
      return [ret] if type(ret) == str else ret
    
   def visitFile_source(self, ctx:TptpParser.File_sourceContext):
      """
      file_source             : 'file(' file_name file_info? ')'; // #INFO ? because file_info may be empty
      """
      file_name = self.visit(ctx.getChild(1)).strip("'\"")
      file_info = None
      if ctx.getChildCount()==4:
         file_info = self.visit(ctx.getChild(2))
      return ("file", (file_name, file_info))
   
   def visitFile_info(self, ctx:TptpParser.File_infoContext):
      """
      file_info               : ',' name;
      """
      return self.visit(ctx.getChild(1))

del TptpVisitor
del TptpParser

