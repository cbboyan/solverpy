from ..domain.grackle import GrackleDomain, _parse_params, _parse_conditions, _parse_forbiddens


class Cvc5BaseDomain(GrackleDomain):

   @property
   def params(self):
      return _parse_params(PARAMS)

   @property
   def defaults(self):
      return DEFAULTS

   @property
   def conditions(self):
      return _parse_conditions(CONDITIONS)

   @property
   def forbiddens(self):
      return _parse_forbiddens(FORBIDDENS)


PARAMS = """
full_saturate_quant {yes,no} [%(full_saturate_quant)s] 
enum_inst_rd {yes,no} [%(enum_inst_rd)s] 
quant_ind {yes,no} [%(quant_ind)s] 
finite_model_find {yes,no} [%(finite_model_find)s] 
macros_quant {yes,no} [%(macros_quant)s] 
macros_quant_mode {all,ground,ground_uf} [%(macros_quant_mode)s] 
e_matching {yes,no} [%(e_matching)s] 
inst_when {full,full_delay,full_last_call,full_delay_last_call,last_call} [%(inst_when)s] 
uf_ss {full,no_minimal,none} [%(uf_ss)s] 
decision {internal,justification,stoponly} [%(decision)s] 
multi_trigger_cache {yes,no} [%(multi_trigger_cache)s] 
multi_trigger_priority {yes,no} [%(multi_trigger_priority)s] 
multi_trigger_when_single {yes,no} [%(multi_trigger_when_single)s] 
multi_trigger_linear {yes,no} [%(multi_trigger_linear)s] 
inst_no_entail {yes,no} [%(inst_no_entail)s] 
pre_skolem_quant {off,on,agg} [%(pre_skolem_quant)s] 
relevant_triggers {yes,no} [%(relevant_triggers)s] 
simplification {none,batch} [%(simplification)s] 
term_db_mode {all,relevant} [%(term_db_mode)s] 
trigger_sel {min,max,min_s_max,min_s_all,all} [%(trigger_sel)s] 
# new ones:
fmf_mbqi {none,fmc} [%(fmf_mbqi)s] 
fmf_bound {yes,no} [%(fmf_bound)s] 
fmf_bound_lazy {yes,no} [%(fmf_bound_lazy)s]
fmf_bound_blast {yes,no} [%(fmf_bound_blast)s]
fmf_fun {yes,no} [%(fmf_fun)s]
fmf_fun_rlv {yes,no} [%(fmf_fun_rlv)s]
# cvc5 new ones:
cegqi_bv {yes,no} [%(cegqi_bv)s]
cegqi_bv_ineq {eq_slack,eq_boundary,keep} [%(cegqi_bv_ineq)s]
cegqi_innermost {yes,no} [%(cegqi_innermost)s]
cegqi_nested_qe {yes,no} [%(cegqi_nested_qe)s]
cegqi {yes,no} [%(cegqi)s]
cegqi_full {yes,no} [%(cegqi_full)s]
cegqi_all {yes,no} [%(cegqi_all)s]
cegqi_multi_inst {yes,no} [%(cegqi_multi_inst)s]
global_negate {yes,no} [%(global_negate)s]
nl_ext_tplanes {yes,no} [%(nl_ext_tplanes)s]
sygus_inst {yes,no} [%(sygus_inst)s]
sygus_inference {yes,no} [%(sygus_inference)s]
sygus_inst_mode {priority_inst,priority_eval,interleave} [%(sygus_inst_mode)s]
sygus_inst_scope {in,out,both} [%(sygus_inst_scope)s]
sygus_inst_term_sel {min,max,both} [%(sygus_inst_term_sel)s]
fmf_type_completion_thresh {100,250,500,750,1000,2500,5000,7500,10000} [%(fmf_type_completion_thresh)s]
# new 2023-11:11
mbqi {yes,no} [%(mbqi)s]
"""
# mbqi {none,fmc,trust} [fmc]  -- `trust` was removed as being incomplete
# fmf_type_completion_thresh [100,10000] [1000]
##removed 2023-11:
# fs_interleave {yes,no} [%(fs_interleave)s] 
# quant_cf {yes,no} [%(quant_cf)s] 
# pre_skolem_quant {yes,no} [%(pre_skolem_quant)s] 
# fmf_bound_int {yes,no} [%(fmf_bound_int)s]
# fmf_fmc_simple {yes,no} [%(fmf_fmc_simple)s]
# fmf_fresh_dc {yes,no} [%(fmf_fresh_dc)s]
# cegqi_model {yes,no} [%(cegqi_model)s]
# fp_exp {yes,no} [%(fp_exp)s]
# fs_sum {yes,no} [%(fs_sum)s]

CONDITIONS = """
macros_quant_mode | macros_quant in {yes}
enum_inst_rd | full_saturate_quant in {yes}
uf_ss | finite_model_find in {yes}
fmf_mbqi | mbqi in {yes}
fmf_bound | finite_model_find in {yes}
fmf_bound_lazy | finite_model_find in {yes}
fmf_bound_blast | finite_model_find in {yes}
fmf_bound_blast | fmf_bound in {yes}
fmf_fun | finite_model_find in {yes}
fmf_fun_rlv | finite_model_find in {yes}
fmf_inst_engine | finite_model_find in {yes}
fmf_bound_lazy | fmf_bound in {yes}
fmf_type_completion_thresh | finite_model_find in {yes}
sygus_inst_mode | sygus_inst in {yes}
sygus_inst_scope | sygus_inst in {yes}
sygus_inst_term_sel | sygus_inst in {yes}
"""

FORBIDDENS = """
#{full_saturate_quant=yes, finite_model_find=yes}
"""

DEFAULTS = {
   'full_saturate_quant': 'no', 
   'enum_inst_rd': 'yes', 
   'quant_ind': 'no', 
   'finite_model_find': 'no', 
   'macros_quant': 'no', 
   'macros_quant_mode': 'ground_uf', 
   'e_matching': 'yes', 
   'inst_when': 'full_last_call', 
   'fmf_inst_engine': 'no', 
   'uf_ss': 'full', 
   'decision': 'internal', 
   'fmf_mbqi': 'fmc', 
   'multi_trigger_cache': 'no', 
   'multi_trigger_priority': 'no', 
   'multi_trigger_when_single': 'no', 
   'multi_trigger_linear': 'yes', 
   'inst_no_entail': 'yes', 
   'quant_cf': 'yes', 
   'pre_skolem_quant': 'off', 
   'relevant_triggers': 'no', 
   'simplification': 'batch', 
   'term_db_mode': 'all', 
   'trigger_sel': 'min',
   'fmf_bound': 'no', 
   'fmf_bound_lazy': 'no', 
   'fmf_bound_blast': 'no', 
   'fmf_fun': 'no', 
   'fmf_fun_rlv': 'no', 
   'fmf_inst_engine': 'yes', 
   'cegqi_bv': 'yes',
   'cegqi_bv_ineq': 'eq_boundary',
   'cegqi_innermost': 'yes',
   'cegqi_nested_qe': 'no',
   'cegqi': 'no',
   'cegqi_full': 'no',
   'cegqi_all':  'no',
   'cegqi_multi_inst': 'no',
   'fp_exp': 'no',
   'fs_sum': 'no',
   'global_negate': 'no',
   'nl_ext_tplanes': 'no',
   'sygus_inst': 'no',
   'sygus_inference': 'no',
   'sygus_inst_mode': 'priority_inst',
   'sygus_inst_scope': 'in',
   'sygus_inst_term_sel': 'min',
   'fmf_type_completion_thresh': '1000',
   'mbqi': 'no',
}

