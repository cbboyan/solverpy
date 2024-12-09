# Generated from Tptp.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
   from .TptpParser import TptpParser
else:
   from TptpParser import TptpParser

# This class defines a complete generic visitor for a parse tree produced by TptpParser.

class TptpDefaultVisitor(ParseTreeVisitor):

   def defaultVisit(self, ctx):
      return self.visitChildren(ctx)

   # Visit a parse tree produced by TptpParser#tptp_file.
   def visitTptp_file(self, ctx:TptpParser.Tptp_fileContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tptp_input.
   def visitTptp_input(self, ctx:TptpParser.Tptp_inputContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#annotated_formula.
   def visitAnnotated_formula(self, ctx:TptpParser.Annotated_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tpi_annotated.
   def visitTpi_annotated(self, ctx:TptpParser.Tpi_annotatedContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tpi_formula.
   def visitTpi_formula(self, ctx:TptpParser.Tpi_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_annotated.
   def visitThf_annotated(self, ctx:TptpParser.Thf_annotatedContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tfx_annotated.
   def visitTfx_annotated(self, ctx:TptpParser.Tfx_annotatedContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_annotated.
   def visitTff_annotated(self, ctx:TptpParser.Tff_annotatedContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tcf_annotated.
   def visitTcf_annotated(self, ctx:TptpParser.Tcf_annotatedContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_annotated.
   def visitFof_annotated(self, ctx:TptpParser.Fof_annotatedContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#cnf_annotated.
   def visitCnf_annotated(self, ctx:TptpParser.Cnf_annotatedContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#annotations.
   def visitAnnotations(self, ctx:TptpParser.AnnotationsContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#formula_role.
   def visitFormula_role(self, ctx:TptpParser.Formula_roleContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_formula.
   def visitThf_formula(self, ctx:TptpParser.Thf_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_logic_formula.
   def visitThf_logic_formula(self, ctx:TptpParser.Thf_logic_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_binary_formula.
   def visitThf_binary_formula(self, ctx:TptpParser.Thf_binary_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_binary_pair.
   def visitThf_binary_pair(self, ctx:TptpParser.Thf_binary_pairContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_binary_tuple.
   def visitThf_binary_tuple(self, ctx:TptpParser.Thf_binary_tupleContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_or_formula.
   def visitThf_or_formula(self, ctx:TptpParser.Thf_or_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_and_formula.
   def visitThf_and_formula(self, ctx:TptpParser.Thf_and_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_apply_formula.
   def visitThf_apply_formula(self, ctx:TptpParser.Thf_apply_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_unitary_formula.
   def visitThf_unitary_formula(self, ctx:TptpParser.Thf_unitary_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_quantified_formula.
   def visitThf_quantified_formula(self, ctx:TptpParser.Thf_quantified_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_quantification.
   def visitThf_quantification(self, ctx:TptpParser.Thf_quantificationContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_variable_list.
   def visitThf_variable_list(self, ctx:TptpParser.Thf_variable_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_variable.
   def visitThf_variable(self, ctx:TptpParser.Thf_variableContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_typed_variable.
   def visitThf_typed_variable(self, ctx:TptpParser.Thf_typed_variableContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_unary_formula.
   def visitThf_unary_formula(self, ctx:TptpParser.Thf_unary_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_atom.
   def visitThf_atom(self, ctx:TptpParser.Thf_atomContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_function.
   def visitThf_function(self, ctx:TptpParser.Thf_functionContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_conn_term.
   def visitThf_conn_term(self, ctx:TptpParser.Thf_conn_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_conditional.
   def visitThf_conditional(self, ctx:TptpParser.Thf_conditionalContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_let.
   def visitThf_let(self, ctx:TptpParser.Thf_letContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_arguments.
   def visitThf_arguments(self, ctx:TptpParser.Thf_argumentsContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_type_formula.
   def visitThf_type_formula(self, ctx:TptpParser.Thf_type_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_typeable_formula.
   def visitThf_typeable_formula(self, ctx:TptpParser.Thf_typeable_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_subtype.
   def visitThf_subtype(self, ctx:TptpParser.Thf_subtypeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_top_level_type.
   def visitThf_top_level_type(self, ctx:TptpParser.Thf_top_level_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_unitary_type.
   def visitThf_unitary_type(self, ctx:TptpParser.Thf_unitary_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_apply_type.
   def visitThf_apply_type(self, ctx:TptpParser.Thf_apply_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_binary_type.
   def visitThf_binary_type(self, ctx:TptpParser.Thf_binary_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_mapping_type.
   def visitThf_mapping_type(self, ctx:TptpParser.Thf_mapping_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_xprod_type.
   def visitThf_xprod_type(self, ctx:TptpParser.Thf_xprod_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_union_type.
   def visitThf_union_type(self, ctx:TptpParser.Thf_union_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_sequent.
   def visitThf_sequent(self, ctx:TptpParser.Thf_sequentContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_tuple.
   def visitThf_tuple(self, ctx:TptpParser.Thf_tupleContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_formula_list.
   def visitThf_formula_list(self, ctx:TptpParser.Thf_formula_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tfx_formula.
   def visitTfx_formula(self, ctx:TptpParser.Tfx_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tfx_logic_formula.
   def visitTfx_logic_formula(self, ctx:TptpParser.Tfx_logic_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_formula.
   def visitTff_formula(self, ctx:TptpParser.Tff_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_logic_formula.
   def visitTff_logic_formula(self, ctx:TptpParser.Tff_logic_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_binary_formula.
   def visitTff_binary_formula(self, ctx:TptpParser.Tff_binary_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_binary_nonassoc.
   def visitTff_binary_nonassoc(self, ctx:TptpParser.Tff_binary_nonassocContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_binary_assoc.
   def visitTff_binary_assoc(self, ctx:TptpParser.Tff_binary_assocContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_or_formula.
   def visitTff_or_formula(self, ctx:TptpParser.Tff_or_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_and_formula.
   def visitTff_and_formula(self, ctx:TptpParser.Tff_and_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_unitary_formula.
   def visitTff_unitary_formula(self, ctx:TptpParser.Tff_unitary_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_quantified_formula.
   def visitTff_quantified_formula(self, ctx:TptpParser.Tff_quantified_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_variable_list.
   def visitTff_variable_list(self, ctx:TptpParser.Tff_variable_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_variable.
   def visitTff_variable(self, ctx:TptpParser.Tff_variableContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_typed_variable.
   def visitTff_typed_variable(self, ctx:TptpParser.Tff_typed_variableContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_unary_formula.
   def visitTff_unary_formula(self, ctx:TptpParser.Tff_unary_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_atomic_formula.
   def visitTff_atomic_formula(self, ctx:TptpParser.Tff_atomic_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_conditional.
   def visitTff_conditional(self, ctx:TptpParser.Tff_conditionalContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_let.
   def visitTff_let(self, ctx:TptpParser.Tff_letContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_let_term_defns.
   def visitTff_let_term_defns(self, ctx:TptpParser.Tff_let_term_defnsContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_let_term_list.
   def visitTff_let_term_list(self, ctx:TptpParser.Tff_let_term_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_let_term_defn.
   def visitTff_let_term_defn(self, ctx:TptpParser.Tff_let_term_defnContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_let_term_binding.
   def visitTff_let_term_binding(self, ctx:TptpParser.Tff_let_term_bindingContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_let_formula_defns.
   def visitTff_let_formula_defns(self, ctx:TptpParser.Tff_let_formula_defnsContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_let_formula_list.
   def visitTff_let_formula_list(self, ctx:TptpParser.Tff_let_formula_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_let_formula_defn.
   def visitTff_let_formula_defn(self, ctx:TptpParser.Tff_let_formula_defnContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_let_formula_binding.
   def visitTff_let_formula_binding(self, ctx:TptpParser.Tff_let_formula_bindingContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_sequent.
   def visitTff_sequent(self, ctx:TptpParser.Tff_sequentContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_formula_tuple.
   def visitTff_formula_tuple(self, ctx:TptpParser.Tff_formula_tupleContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_formula_tuple_list.
   def visitTff_formula_tuple_list(self, ctx:TptpParser.Tff_formula_tuple_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_typed_atom.
   def visitTff_typed_atom(self, ctx:TptpParser.Tff_typed_atomContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_subtype.
   def visitTff_subtype(self, ctx:TptpParser.Tff_subtypeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_top_level_type.
   def visitTff_top_level_type(self, ctx:TptpParser.Tff_top_level_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tf1_quantified_type.
   def visitTf1_quantified_type(self, ctx:TptpParser.Tf1_quantified_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_monotype.
   def visitTff_monotype(self, ctx:TptpParser.Tff_monotypeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_unitary_type.
   def visitTff_unitary_type(self, ctx:TptpParser.Tff_unitary_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_atomic_type.
   def visitTff_atomic_type(self, ctx:TptpParser.Tff_atomic_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_type_arguments.
   def visitTff_type_arguments(self, ctx:TptpParser.Tff_type_argumentsContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_mapping_type.
   def visitTff_mapping_type(self, ctx:TptpParser.Tff_mapping_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_xprod_type.
   def visitTff_xprod_type(self, ctx:TptpParser.Tff_xprod_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tcf_formula.
   def visitTcf_formula(self, ctx:TptpParser.Tcf_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tcf_logic_formula.
   def visitTcf_logic_formula(self, ctx:TptpParser.Tcf_logic_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tcf_quantified_formula.
   def visitTcf_quantified_formula(self, ctx:TptpParser.Tcf_quantified_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_formula.
   def visitFof_formula(self, ctx:TptpParser.Fof_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_logic_formula.
   def visitFof_logic_formula(self, ctx:TptpParser.Fof_logic_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_binary_formula.
   def visitFof_binary_formula(self, ctx:TptpParser.Fof_binary_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_binary_nonassoc.
   def visitFof_binary_nonassoc(self, ctx:TptpParser.Fof_binary_nonassocContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_binary_assoc.
   def visitFof_binary_assoc(self, ctx:TptpParser.Fof_binary_assocContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_or_formula.
   def visitFof_or_formula(self, ctx:TptpParser.Fof_or_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_and_formula.
   def visitFof_and_formula(self, ctx:TptpParser.Fof_and_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_unitary_formula.
   def visitFof_unitary_formula(self, ctx:TptpParser.Fof_unitary_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_quantified_formula.
   def visitFof_quantified_formula(self, ctx:TptpParser.Fof_quantified_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_variable_list.
   def visitFof_variable_list(self, ctx:TptpParser.Fof_variable_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_unary_formula.
   def visitFof_unary_formula(self, ctx:TptpParser.Fof_unary_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_infix_unary.
   def visitFof_infix_unary(self, ctx:TptpParser.Fof_infix_unaryContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_atomic_formula.
   def visitFof_atomic_formula(self, ctx:TptpParser.Fof_atomic_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_plain_atomic_formula.
   def visitFof_plain_atomic_formula(self, ctx:TptpParser.Fof_plain_atomic_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_defined_atomic_formula.
   def visitFof_defined_atomic_formula(self, ctx:TptpParser.Fof_defined_atomic_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_defined_plain_formula.
   def visitFof_defined_plain_formula(self, ctx:TptpParser.Fof_defined_plain_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_defined_infix_formula.
   def visitFof_defined_infix_formula(self, ctx:TptpParser.Fof_defined_infix_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_system_atomic_formula.
   def visitFof_system_atomic_formula(self, ctx:TptpParser.Fof_system_atomic_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_plain_term.
   def visitFof_plain_term(self, ctx:TptpParser.Fof_plain_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_defined_term.
   def visitFof_defined_term(self, ctx:TptpParser.Fof_defined_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_defined_atomic_term.
   def visitFof_defined_atomic_term(self, ctx:TptpParser.Fof_defined_atomic_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_defined_plain_term.
   def visitFof_defined_plain_term(self, ctx:TptpParser.Fof_defined_plain_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_system_term.
   def visitFof_system_term(self, ctx:TptpParser.Fof_system_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_arguments.
   def visitFof_arguments(self, ctx:TptpParser.Fof_argumentsContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_term.
   def visitFof_term(self, ctx:TptpParser.Fof_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_function_term.
   def visitFof_function_term(self, ctx:TptpParser.Fof_function_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_conditional_term.
   def visitTff_conditional_term(self, ctx:TptpParser.Tff_conditional_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_let_term.
   def visitTff_let_term(self, ctx:TptpParser.Tff_let_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_tuple_term.
   def visitTff_tuple_term(self, ctx:TptpParser.Tff_tuple_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_sequent.
   def visitFof_sequent(self, ctx:TptpParser.Fof_sequentContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_formula_tuple.
   def visitFof_formula_tuple(self, ctx:TptpParser.Fof_formula_tupleContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_formula_tuple_list.
   def visitFof_formula_tuple_list(self, ctx:TptpParser.Fof_formula_tuple_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#cnf_formula.
   def visitCnf_formula(self, ctx:TptpParser.Cnf_formulaContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#cnf_disjunction.
   def visitCnf_disjunction(self, ctx:TptpParser.Cnf_disjunctionContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#cnf_literal.
   def visitCnf_literal(self, ctx:TptpParser.Cnf_literalContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_quantifier.
   def visitThf_quantifier(self, ctx:TptpParser.Thf_quantifierContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#th0_quantifier.
   def visitTh0_quantifier(self, ctx:TptpParser.Th0_quantifierContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#th1_quantifier.
   def visitTh1_quantifier(self, ctx:TptpParser.Th1_quantifierContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_pair_connective.
   def visitThf_pair_connective(self, ctx:TptpParser.Thf_pair_connectiveContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#thf_unary_connective.
   def visitThf_unary_connective(self, ctx:TptpParser.Thf_unary_connectiveContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#th1_unary_connective.
   def visitTh1_unary_connective(self, ctx:TptpParser.Th1_unary_connectiveContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#tff_pair_connective.
   def visitTff_pair_connective(self, ctx:TptpParser.Tff_pair_connectiveContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#fof_quantifier.
   def visitFof_quantifier(self, ctx:TptpParser.Fof_quantifierContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#binary_connective.
   def visitBinary_connective(self, ctx:TptpParser.Binary_connectiveContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#assoc_connective.
   def visitAssoc_connective(self, ctx:TptpParser.Assoc_connectiveContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#unary_connective.
   def visitUnary_connective(self, ctx:TptpParser.Unary_connectiveContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#type_constant.
   def visitType_constant(self, ctx:TptpParser.Type_constantContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#type_functor.
   def visitType_functor(self, ctx:TptpParser.Type_functorContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#defined_type.
   def visitDefined_type(self, ctx:TptpParser.Defined_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#system_type.
   def visitSystem_type(self, ctx:TptpParser.System_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#atom.
   def visitAtom(self, ctx:TptpParser.AtomContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#untyped_atom.
   def visitUntyped_atom(self, ctx:TptpParser.Untyped_atomContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#defined_proposition.
   def visitDefined_proposition(self, ctx:TptpParser.Defined_propositionContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#defined_predicate.
   def visitDefined_predicate(self, ctx:TptpParser.Defined_predicateContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#defined_infix_pred.
   def visitDefined_infix_pred(self, ctx:TptpParser.Defined_infix_predContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#constant.
   def visitConstant(self, ctx:TptpParser.ConstantContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#functor.
   def visitFunctor(self, ctx:TptpParser.FunctorContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#system_constant.
   def visitSystem_constant(self, ctx:TptpParser.System_constantContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#system_functor.
   def visitSystem_functor(self, ctx:TptpParser.System_functorContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#defined_constant.
   def visitDefined_constant(self, ctx:TptpParser.Defined_constantContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#defined_functor.
   def visitDefined_functor(self, ctx:TptpParser.Defined_functorContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#defined_term.
   def visitDefined_term(self, ctx:TptpParser.Defined_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#variable.
   def visitVariable(self, ctx:TptpParser.VariableContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#source.
   def visitSource(self, ctx:TptpParser.SourceContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#sources.
   def visitSources(self, ctx:TptpParser.SourcesContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#dag_source.
   def visitDag_source(self, ctx:TptpParser.Dag_sourceContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#inference_record.
   def visitInference_record(self, ctx:TptpParser.Inference_recordContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#inference_rule.
   def visitInference_rule(self, ctx:TptpParser.Inference_ruleContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#inference_parents.
   def visitInference_parents(self, ctx:TptpParser.Inference_parentsContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#parent_list.
   def visitParent_list(self, ctx:TptpParser.Parent_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#parent_info.
   def visitParent_info(self, ctx:TptpParser.Parent_infoContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#parent_details.
   def visitParent_details(self, ctx:TptpParser.Parent_detailsContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#internal_source.
   def visitInternal_source(self, ctx:TptpParser.Internal_sourceContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#intro_type.
   def visitIntro_type(self, ctx:TptpParser.Intro_typeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#external_source.
   def visitExternal_source(self, ctx:TptpParser.External_sourceContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#file_source.
   def visitFile_source(self, ctx:TptpParser.File_sourceContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#file_info.
   def visitFile_info(self, ctx:TptpParser.File_infoContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#theory.
   def visitTheory(self, ctx:TptpParser.TheoryContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#theory_name.
   def visitTheory_name(self, ctx:TptpParser.Theory_nameContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#creator_source.
   def visitCreator_source(self, ctx:TptpParser.Creator_sourceContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#creator_name.
   def visitCreator_name(self, ctx:TptpParser.Creator_nameContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#optional_info.
   def visitOptional_info(self, ctx:TptpParser.Optional_infoContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#useful_info.
   def visitUseful_info(self, ctx:TptpParser.Useful_infoContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#info_items.
   def visitInfo_items(self, ctx:TptpParser.Info_itemsContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#info_item.
   def visitInfo_item(self, ctx:TptpParser.Info_itemContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#formula_item.
   def visitFormula_item(self, ctx:TptpParser.Formula_itemContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#description_item.
   def visitDescription_item(self, ctx:TptpParser.Description_itemContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#iquote_item.
   def visitIquote_item(self, ctx:TptpParser.Iquote_itemContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#inference_item.
   def visitInference_item(self, ctx:TptpParser.Inference_itemContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#inference_status.
   def visitInference_status(self, ctx:TptpParser.Inference_statusContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#status_value.
   def visitStatus_value(self, ctx:TptpParser.Status_valueContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#inference_info.
   def visitInference_info(self, ctx:TptpParser.Inference_infoContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#assumptions_record.
   def visitAssumptions_record(self, ctx:TptpParser.Assumptions_recordContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#refutation.
   def visitRefutation(self, ctx:TptpParser.RefutationContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#new_symbol_record.
   def visitNew_symbol_record(self, ctx:TptpParser.New_symbol_recordContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#new_symbol_list.
   def visitNew_symbol_list(self, ctx:TptpParser.New_symbol_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#principal_symbol.
   def visitPrincipal_symbol(self, ctx:TptpParser.Principal_symbolContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#include.
   def visitInclude(self, ctx:TptpParser.IncludeContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#formula_selection.
   def visitFormula_selection(self, ctx:TptpParser.Formula_selectionContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#name_list.
   def visitName_list(self, ctx:TptpParser.Name_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#general_term.
   def visitGeneral_term(self, ctx:TptpParser.General_termContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#general_data.
   def visitGeneral_data(self, ctx:TptpParser.General_dataContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#general_function.
   def visitGeneral_function(self, ctx:TptpParser.General_functionContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#formula_data.
   def visitFormula_data(self, ctx:TptpParser.Formula_dataContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#general_list.
   def visitGeneral_list(self, ctx:TptpParser.General_listContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#general_terms.
   def visitGeneral_terms(self, ctx:TptpParser.General_termsContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#name.
   def visitName(self, ctx:TptpParser.NameContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#atomic_word.
   def visitAtomic_word(self, ctx:TptpParser.Atomic_wordContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#atomic_defined_word.
   def visitAtomic_defined_word(self, ctx:TptpParser.Atomic_defined_wordContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#atomic_system_word.
   def visitAtomic_system_word(self, ctx:TptpParser.Atomic_system_wordContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#number.
   def visitNumber(self, ctx:TptpParser.NumberContext):
      return self.defaultVisit(ctx)


   # Visit a parse tree produced by TptpParser#file_name.
   def visitFile_name(self, ctx:TptpParser.File_nameContext):
      return self.defaultVisit(ctx)

del TptpParser

