
PARAMS = """
ackermann {yes,no} [%(ackermann)s]
cbqi {yes,no} [%(cbqi)s]
cbqi_all_conflict {yes,no} [%(cbqi_all_conflict)s]
cbqi_mode {conflict,prop_eq} [%(cbqi_mode)s]
cegis_sample {none,use,trust} [%(cegis_sample)s]
cegqi {yes,no} [%(cegqi)s]
cegqi_bv {yes,no} [%(cegqi_bv)s]
cegqi_bv_ineq {eq_slack,eq_boundary,keep} [%(cegqi_bv_ineq)s]
cegqi_inf_int {yes,no} [%(cegqi_inf_int)s]
cegqi_inf_real {yes,no} [%(cegqi_inf_real)s]
cegqi_innermost {yes,no} [%(cegqi_innermost)s]
cegqi_midpoint {yes,no} [%(cegqi_midpoint)s]
cegqi_nested_qe {yes,no} [%(cegqi_nested_qe)s]
check_abducts {yes,no} [%(check_abducts)s]
check_interpolants {yes,no} [%(check_interpolants)s]
check_proofs {yes,no} [%(check_proofs)s]
check_synth_sol {yes,no} [%(check_synth_sol)s]
check_unsat_cores {yes,no} [%(check_unsat_cores)s]
decision {internal,justification,stoponly} [%(decision)s]
e_matching {yes,no} [%(e_matching)s]
elim_taut_quant {yes,no} [%(elim_taut_quant)s]
enum_inst {yes,no} [%(enum_inst)s]
enum_inst_interleave {yes,no} [%(enum_inst_interleave)s]
enum_inst_sum {yes,no} [%(enum_inst_sum)s]
ext_rew_prep {off,use,agg} [%(ext_rew_prep)s]
ext_rewrite_quant {yes,no} [%(ext_rewrite_quant)s]
finite_model_find {yes,no} [%(finite_model_find)s]
fmf_bound {yes,no} [%(fmf_bound)s]
fmf_fun {yes,no} [%(fmf_fun)s]
fmf_fun_rlv {yes,no} [%(fmf_fun_rlv)s]
full_saturate_quant {yes,no} [%(full_saturate_quant)s]
ho_elim {yes,no} [%(ho_elim)s]
ho_elim_store_ax {yes,no} [%(ho_elim_store_ax)s]
ieval {off,use,use_learn} [%(ieval)s]
inst_no_entail {yes,no} [%(inst_no_entail)s]
inst_when {full,full_delay,full_last_call,full_delay_last_call,last_call} [%(inst_when)s]
interpolants_mode {default,assumptions,conjecture,shared,all} [%(interpolants_mode)s]
ite_lift_quant {none,simple,all} [%(ite_lift_quant)s]
learned_rewrite {yes,no} [%(learned_rewrite)s]
macros_quant {yes,no} [%(macros_quant)s]
macros_quant_mode {all,ground,ground_uf} [%(macros_quant_mode)s]
mbqi_one_inst_per_round {yes,no} [%(mbqi_one_inst_per_round)s]
miniscope_quant {off,conj,fv,conj_and_fv,agg} [%(miniscope_quant)s]
model_cores {none,simple,non_implied} [%(model_cores)s]
multi_trigger_cache {yes,no} [%(multi_trigger_cache)s]
multi_trigger_linear {yes,no} [%(multi_trigger_linear)s]
multi_trigger_priority {yes,no} [%(multi_trigger_priority)s]
multi_trigger_when_single {yes,no} [%(multi_trigger_when_single)s]
pre_skolem_quant {off,on,agg} [%(pre_skolem_quant)s]
prenex_quant_user {yes,no} [%(prenex_quant_user)s]
prenex_quant {none,simple,norm} [%(prenex_quant)s]
produce_abducts {yes,no} [%(produce_abducts)s]
produce_assertions {yes,no} [%(produce_assertions)s]
produce_assignments {yes,no} [%(produce_assignments)s]
produce_difficulty {yes,no} [%(produce_difficulty)s]
produce_interpolants {yes,no} [%(produce_interpolants)s]
produce_learned_literals {yes,no} [%(produce_learned_literals)s]
produce_proofs {yes,no} [%(produce_proofs)s]
produce_unsat_assumptions {yes,no} [%(produce_unsat_assumptions)s]
produce_unsat_cores {yes,no} [%(produce_unsat_cores)s]
quant_alpha_equiv {yes,no} [%(quant_alpha_equiv)s]
quant_dsplit {none,default,agg} [%(quant_dsplit)s]
relevant_triggers {yes,no} [%(relevant_triggers)s]
simplification {none,batch} [%(simplification)s]
static_learning {yes,no} [%(static_learning)s]
sygus {yes,no} [%(sygus)s]
sygus_add_const_grammar {yes,no} [%(sygus_add_const_grammar)s]
sygus_core_connective {yes,no} [%(sygus_core_connective)s]
sygus_enum {smart,fast,random,var_agnostic,auto} [%(sygus_enum)s]
sygus_eval_unfold {none,single,single_bool,multi} [%(sygus_eval_unfold)s]
sygus_grammar_cons {simple,any_const,any_term,any_term_concise} [%(sygus_grammar_cons)s]
sygus_inst {yes,no} [%(sygus_inst)s]
sygus_inv_templ {none,pre,post} [%(sygus_inv_templ)s]
sygus_min_grammar {yes,no} [%(sygus_min_grammar)s]
sygus_out {status,status_and_def,sygus_standard} [%(sygus_out)s]
sygus_pbe {yes,no} [%(sygus_pbe)s]
sygus_repair_const {yes,no} [%(sygus_repair_const)s]
sygus_si_abort {yes,no} [%(sygus_si_abort)s]
sygus_si_rcons {none,try,all_limit,all} [%(sygus_si_rcons)s]
sygus_si {none,use,all} [%(sygus_si)s]
sygus_stream {yes,no} [%(sygus_stream)s]
sygus_unif_pi {none,complete,cond_enum,cond_enum_igain} [%(sygus_unif_pi)s]
term_db_mode {all,relevant} [%(term_db_mode)s]
trigger_sel {min,max,min_s_max,min_s_all,all} [%(trigger_sel)s]
uf_lazy_ll {yes,no} [%(uf_lazy_ll)s]
uf_ss_fair {yes,no} [%(uf_ss_fair)s]
uf_ss {full,no_minimal,none} [%(uf_ss)s]
unconstrained_simp {yes,no} [%(unconstrained_simp)s]
user_pat {use,trust,strict,resort,ignore,interleave} [%(user_pat)s]
var_elim_quant {yes,no} [%(var_elim_quant)s]
var_ineq_elim_quant {yes,no} [%(var_ineq_elim_quant)s]

cbqi_eager_check_rd {yes,no} [%(cbqi_eager_check_rd)s]
cbqi_eager_test {yes,no} [%(cbqi_eager_test)s]
cbqi_skip_rd {yes,no} [%(cbqi_skip_rd)s]
cbqi_tconstraint {yes,no} [%(cbqi_tconstraint)s]
cbqi_vo_exp {yes,no} [%(cbqi_vo_exp)s]
mbqi {yes,no} [%(mbqi)s]
mbqi_interleave {yes,no} [%(mbqi_interleave)s]
"""

CONDITIONS = """
cbqi_all_conflict | cbqi in {yes}
cbqi_mode | cbqi in {yes}
cegqi_bv | cegqi in {yes}
cegqi_bv_ineq | cegqi_bv in {yes}
cegqi_inf_int | cegqi in {yes}
cegqi_inf_real | cegqi in {yes}
cegqi_innermost | cegqi in {yes}
cegqi_midpoint | cegqi in {yes}
cegqi_nested_qe | cegqi in {yes}
enum_inst_interleave | enum_inst in {yes}
enum_inst_sum | enum_inst in {yes}
fmf_fun_rlv | fmf_fun in {yes}
ho_elim_store_ax | ho_elim in {yes}
macros_quant_mode | macros_quant in {yes}
sygus_add_const_grammar | sygus in {yes}
sygus_core_connective | sygus in {yes}
sygus_enum | sygus in {yes}
sygus_eval_unfold | sygus in {yes}
sygus_grammar_cons | sygus in {yes}
sygus_inst | sygus in {yes}
sygus_inv_templ | sygus in {yes}
sygus_min_grammar | sygus in {yes}
sygus_out | sygus in {yes}
sygus_pbe | sygus in {yes}
sygus_repair_const | sygus in {yes}
sygus_si_abort | sygus in {yes}
sygus_si_rcons | sygus in {yes}
sygus_si | sygus in {yes}
sygus_stream | sygus in {yes}
sygus_unif_pi | sygus in {yes}
sygus_verify_timeout | sygus in {yes}

fmf_bound | finite_model_find in {yes}
fmf_fun | finite_model_find in {yes}

cbqi_eager_check_rd | cbqi in {yes}
cbqi_eager_test | cbqi in {yes}
cbqi_skip_rd | cbqi in {yes}
cbqi_tconstraint | cbqi in {yes}
cbqi_vo_exp | cbqi in {yes}
mbqi_interleave | mbqi in {yes}
mbqi_one_inst_per_round | mbqi in {yes}
"""

#{full_saturate_quant=yes, enum_inst=no}
#{full_saturate_quant=no, enum_inst=yes}
FORBIDDENS = """
"""

DEFAULTS = {
   'ackermann': 'no',
   'cbqi': 'yes',
   'cbqi_all_conflict': 'no',
   'cbqi_mode': 'prop_eq',
   'cegis_sample': 'none',
   'cegqi': 'no',
   'cegqi_bv': 'yes',
   'cegqi_bv_ineq': 'eq_boundary',
   'cegqi_inf_int': 'no',
   'cegqi_inf_real': 'no',
   'cegqi_innermost': 'yes',
   'cegqi_midpoint': 'no',
   'cegqi_nested_qe': 'no',
   'check_abducts': 'no',
   'check_interpolants': 'no',
   'check_proofs': 'no',
   'check_synth_sol': 'no',
   'check_unsat_cores': 'no',
   'decision': 'internal',
   'e_matching': 'yes',
   'elim_taut_quant': 'yes',
   'enum_inst': 'no',
   'enum_inst_interleave': 'no',
   'enum_inst_sum': 'no',
   'ext_rew_prep': 'off',
   'ext_rewrite_quant': 'no',
   'finite_model_find': 'no',
   'fmf_bound': 'no',
   'fmf_fun': 'no',
   'fmf_fun_rlv': 'no',
   'full_saturate_quant': 'no',
   'ho_elim': 'no',
   'ho_elim_store_ax': 'yes',
   'ieval': 'use',
   'inst_no_entail': 'yes',
   'inst_when': 'full_last_call',
   'interpolants_mode': 'default',
   'ite_lift_quant': 'simple',
   'learned_rewrite': 'no',
   'macros_quant': 'no',
   'macros_quant_mode': 'ground_uf',
   'mbqi_one_inst_per_round': 'no',
   'miniscope_quant': 'conj_and_fv',
   'model_cores': 'none',
   'multi_trigger_cache': 'no',
   'multi_trigger_linear': 'yes',
   'multi_trigger_priority': 'no',
   'multi_trigger_when_single': 'no',
   'pre_skolem_quant': 'off',
   'prenex_quant_user': 'no',
   'prenex_quant': 'simple',
   'produce_abducts': 'no',
   'produce_assertions': 'yes',
   'produce_assignments': 'no',
   'produce_difficulty': 'no',
   'produce_interpolants': 'no',
   'produce_learned_literals': 'no',
   'produce_proofs': 'no',
   'produce_unsat_assumptions': 'no',
   'produce_unsat_cores': 'no',
   'quant_alpha_equiv': 'yes',
   'quant_dsplit': 'default',
   'relevant_triggers': 'no',
   'simplification': 'batch',
   'static_learning': 'yes',
   'sygus': 'no',
   'sygus_add_const_grammar': 'yes',
   'sygus_core_connective': 'yes',
   'sygus_enum': 'auto',
   'sygus_eval_unfold': 'single_bool',
   'sygus_grammar_cons': 'simple',
   'sygus_inst': 'no',
   'sygus_inv_templ': 'post',
   'sygus_min_grammar': 'yes',
   'sygus_out': 'sygus_standard',
   'sygus_pbe': 'yes',
   'sygus_repair_const': 'no',
   'sygus_si_abort': 'no',
   'sygus_si_rcons': 'all',
   'sygus_si': 'none',
   'sygus_stream': 'no',
   'sygus_unif_pi': 'none',
   'term_db_mode': 'all',
   'trigger_sel': 'min',
   'uf_lazy_ll': 'yes',
   'uf_ss_fair': 'yes',
   'uf_ss': 'full',
   'unconstrained_simp': 'no',
   'user_pat': 'trust',
   'var_elim_quant': 'yes',
   'var_ineq_elim_quant': 'yes',

   'cbqi_eager_check_rd': 'yes',
   'cbqi_eager_test': 'yes',
   'cbqi_skip_rd': 'no',
   'cbqi_tconstraint': 'no',
   'cbqi_vo_exp': 'no',
   'mbqi': 'no',
   'mbqi_interleave': 'no',
}

