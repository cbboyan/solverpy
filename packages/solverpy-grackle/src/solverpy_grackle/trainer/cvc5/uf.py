
PARAMS = """
abstract_values {yes,no} [%(abstract_values)s]
ackermann {yes,no} [%(ackermann)s]
bv_to_int_use_pow2 {yes,no} [%(bv_to_int_use_pow2)s]
cbqi {yes,no} [%(cbqi)s]
cbqi_all_conflict {yes,no} [%(cbqi_all_conflict)s]
cbqi_eager_check_rd {yes,no} [%(cbqi_eager_check_rd)s]
cbqi_eager_test {yes,no} [%(cbqi_eager_test)s]
cbqi_mode {conflict,prop_eq} [%(cbqi_mode)s]
cbqi_skip_rd {yes,no} [%(cbqi_skip_rd)s]
cbqi_tconstraint {yes,no} [%(cbqi_tconstraint)s]
cbqi_vo_exp {yes,no} [%(cbqi_vo_exp)s]
cegis_sample {none,use,trust} [%(cegis_sample)s]
cegqi {yes,no} [%(cegqi)s]
cegqi_all {yes,no} [%(cegqi_all)s]
cegqi_bv {yes,no} [%(cegqi_bv)s]
cegqi_bv_concat_inv {yes,no} [%(cegqi_bv_concat_inv)s]
cegqi_bv_ineq {eq_slack,eq_boundary,keep} [%(cegqi_bv_ineq)s]
cegqi_bv_interleave_value {yes,no} [%(cegqi_bv_interleave_value)s]
cegqi_bv_linear {yes,no} [%(cegqi_bv_linear)s]
cegqi_bv_rm_extract {yes,no} [%(cegqi_bv_rm_extract)s]
cegqi_bv_solve_nl {yes,no} [%(cegqi_bv_solve_nl)s]
cegqi_full {yes,no} [%(cegqi_full)s]
cegqi_inf_int {yes,no} [%(cegqi_inf_int)s]
cegqi_inf_real {yes,no} [%(cegqi_inf_real)s]
cegqi_innermost {yes,no} [%(cegqi_innermost)s]
cegqi_midpoint {yes,no} [%(cegqi_midpoint)s]
cegqi_min_bounds {yes,no} [%(cegqi_min_bounds)s]
cegqi_multi_inst {yes,no} [%(cegqi_multi_inst)s]
cegqi_nested_qe {yes,no} [%(cegqi_nested_qe)s]
cegqi_nopt {yes,no} [%(cegqi_nopt)s]
cegqi_round_up_lia {yes,no} [%(cegqi_round_up_lia)s]
check_abducts {yes,no} [%(check_abducts)s]
check_interpolants {yes,no} [%(check_interpolants)s]
check_models {yes,no} [%(check_models)s]
check_proofs {yes,no} [%(check_proofs)s]
check_synth_sol {yes,no} [%(check_synth_sol)s]
check_unsat_cores {yes,no} [%(check_unsat_cores)s]
cond_var_split_quant {off,on,agg} [%(cond_var_split_quant)s]
conjecture_gen {yes,no} [%(conjecture_gen)s]
cons_exp_triggers {yes,no} [%(cons_exp_triggers)s]
debug_check_models {yes,no} [%(debug_check_models)s]
decision {internal,justification,stoponly} [%(decision)s]
deep_restart {none,input,input_and_solvable,input_and_prop,all} [%(deep_restart)s]
difficulty_mode {lemma_literal,lemma_literal_all,model_check} [%(difficulty_mode)s]
dt_stc_ind {yes,no} [%(dt_stc_ind)s]
dt_var_exp_quant {yes,no} [%(dt_var_exp_quant)s]
e_matching {yes,no} [%(e_matching)s]
eager_arith_bv_conv {yes,no} [%(eager_arith_bv_conv)s]
early_ite_removal {yes,no} [%(early_ite_removal)s]
elim_taut_quant {yes,no} [%(elim_taut_quant)s]
enum_inst {yes,no} [%(enum_inst)s]
enum_inst_interleave {yes,no} [%(enum_inst_interleave)s]
enum_inst_rd {yes,no} [%(enum_inst_rd)s]
enum_inst_stratify {yes,no} [%(enum_inst_stratify)s]
enum_inst_sum {yes,no} [%(enum_inst_sum)s]
ext_rew_prep {off,use,agg} [%(ext_rew_prep)s]
ext_rewrite_quant {yes,no} [%(ext_rewrite_quant)s]
finite_model_find {yes,no} [%(finite_model_find)s]
fmf_bound {yes,no} [%(fmf_bound)s]
fmf_bound_blast {yes,no} [%(fmf_bound_blast)s]
fmf_bound_lazy {yes,no} [%(fmf_bound_lazy)s]
fmf_fun {yes,no} [%(fmf_fun)s]
fmf_fun_rlv {yes,no} [%(fmf_fun_rlv)s]
fmf_mbqi {none,fmc} [%(fmf_mbqi)s]
foreign_theory_rewrite {yes,no} [%(foreign_theory_rewrite)s]
full_saturate_quant {yes,no} [%(full_saturate_quant)s]
global_negate {yes,no} [%(global_negate)s]
ho_elim {yes,no} [%(ho_elim)s]
ho_elim_store_ax {yes,no} [%(ho_elim_store_ax)s]
ho_matching {yes,no} [%(ho_matching)s]
ho_merge_term_db {yes,no} [%(ho_merge_term_db)s]
iand_mode {value,sum,bitwise} [%(iand_mode)s]
ieval {off,use,use_learn} [%(ieval)s]
increment_triggers {yes,no} [%(increment_triggers)s]
inst_no_entail {yes,no} [%(inst_no_entail)s]
inst_when {full,full_delay,full_last_call,full_delay_last_call,last_call} [%(inst_when)s]
int_wf_ind {yes,no} [%(int_wf_ind)s]
interpolants_mode {default,assumptions,conjecture,shared,all} [%(interpolants_mode)s]
ite_dtt_split_quant {yes,no} [%(ite_dtt_split_quant)s]
ite_lift_quant {none,simple,all} [%(ite_lift_quant)s]
ite_simp {yes,no} [%(ite_simp)s]
jh_rlv_order {yes,no} [%(jh_rlv_order)s]
jh_skolem_rlv {assert,always} [%(jh_skolem_rlv)s]
jh_skolem {first,last} [%(jh_skolem)s]
learned_rewrite {yes,no} [%(learned_rewrite)s]
literal_matching {none,use,agg_predicate,agg} [%(literal_matching)s]
macros_quant {yes,no} [%(macros_quant)s]
macros_quant_mode {all,ground,ground_uf} [%(macros_quant_mode)s]
mbqi {yes,no} [%(mbqi)s]
mbqi_interleave {yes,no} [%(mbqi_interleave)s]
mbqi_one_inst_per_round {yes,no} [%(mbqi_one_inst_per_round)s]
minimal_unsat_cores {yes,no} [%(minimal_unsat_cores)s]
minisat_dump_dimacs {yes,no} [%(minisat_dump_dimacs)s]
minisat_simplification {all,clause_elim,none} [%(minisat_simplification)s]
miniscope_quant {off,conj,fv,conj_and_fv,agg} [%(miniscope_quant)s]
model_cores {none,simple,non_implied} [%(model_cores)s]
model_var_elim_uneval {yes,no} [%(model_var_elim_uneval)s]
multi_trigger_cache {yes,no} [%(multi_trigger_cache)s]
multi_trigger_linear {yes,no} [%(multi_trigger_linear)s]
multi_trigger_priority {yes,no} [%(multi_trigger_priority)s]
multi_trigger_when_single {yes,no} [%(multi_trigger_when_single)s]
on_repeat_ite_simp {yes,no} [%(on_repeat_ite_simp)s]
oracles {yes,no} [%(oracles)s]
partial_triggers {yes,no} [%(partial_triggers)s]
pool_inst {yes,no} [%(pool_inst)s]
pre_skolem_quant_nested {yes,no} [%(pre_skolem_quant_nested)s]
pre_skolem_quant {off,on,agg} [%(pre_skolem_quant)s]
prenex_quant_user {yes,no} [%(prenex_quant_user)s]
prenex_quant {none,simple,norm} [%(prenex_quant)s]
preregister_mode {eager,lazy} [%(preregister_mode)s]
print_cores_full {yes,no} [%(print_cores_full)s]
print_inst_full {yes,no} [%(print_inst_full)s]
print_inst {list,num} [%(print_inst)s]
produce_abducts {yes,no} [%(produce_abducts)s]
produce_assertions {yes,no} [%(produce_assertions)s]
produce_assignments {yes,no} [%(produce_assignments)s]
produce_difficulty {yes,no} [%(produce_difficulty)s]
produce_interpolants {yes,no} [%(produce_interpolants)s]
produce_learned_literals {yes,no} [%(produce_learned_literals)s]
produce_models {yes,no} [%(produce_models)s]
produce_proofs {yes,no} [%(produce_proofs)s]
produce_unsat_assumptions {yes,no} [%(produce_unsat_assumptions)s]
produce_unsat_cores {yes,no} [%(produce_unsat_cores)s]
proof_mode {off,pp_only,sat_proof,full_proof} [%(proof_mode)s]
purify_triggers {yes,no} [%(purify_triggers)s]
quant_alpha_equiv {yes,no} [%(quant_alpha_equiv)s]
quant_dsplit {none,default,agg} [%(quant_dsplit)s]
quant_fun_wd {yes,no} [%(quant_fun_wd)s]
quant_ind {yes,no} [%(quant_ind)s]
quant_rep_mode {ee,first,depth} [%(quant_rep_mode)s]
register_quant_body_terms {yes,no} [%(register_quant_body_terms)s]
relational_triggers {yes,no} [%(relational_triggers)s]
relevant_triggers {yes,no} [%(relevant_triggers)s]
repeat_simp {yes,no} [%(repeat_simp)s]
simp_ite_compress {yes,no} [%(simp_ite_compress)s]
simp_with_care {yes,no} [%(simp_with_care)s]
simplification_bcp {yes,no} [%(simplification_bcp)s]
simplification {none,batch} [%(simplification)s]
solve_bv_as_int {off,sum,iand,bv,bitwise} [%(solve_bv_as_int)s]
solve_real_as_int {yes,no} [%(solve_real_as_int)s]
sort_inference {yes,no} [%(sort_inference)s]
static_learning {yes,no} [%(static_learning)s]
sygus {yes,no} [%(sygus)s]
sygus_add_const_grammar {yes,no} [%(sygus_add_const_grammar)s]
sygus_arg_relevant {yes,no} [%(sygus_arg_relevant)s]
sygus_auto_unfold {yes,no} [%(sygus_auto_unfold)s]
sygus_bool_ite_return_const {yes,no} [%(sygus_bool_ite_return_const)s]
sygus_core_connective {yes,no} [%(sygus_core_connective)s]
sygus_crepair_abort {yes,no} [%(sygus_crepair_abort)s]
sygus_enum {smart,fast,random,var_agnostic,auto} [%(sygus_enum)s]
sygus_eval_unfold {none,single,single_bool,multi} [%(sygus_eval_unfold)s]
sygus_filter_sol_rev {yes,no} [%(sygus_filter_sol_rev)s]
sygus_filter_sol {none,strong,weak} [%(sygus_filter_sol)s]
sygus_grammar_cons {simple,any_const,any_term,any_term_concise} [%(sygus_grammar_cons)s]
sygus_grammar_norm {yes,no} [%(sygus_grammar_norm)s]
sygus_grammar_use_disj {yes,no} [%(sygus_grammar_use_disj)s]
sygus_inference {yes,no} [%(sygus_inference)s]
sygus_inst {yes,no} [%(sygus_inst)s]
sygus_inst_mode {priority_inst,priority_eval,interleave} [%(sygus_inst_mode)s]
sygus_inst_scope {in,out,both} [%(sygus_inst_scope)s]
sygus_inst_term_sel {min,max,both} [%(sygus_inst_term_sel)s]
sygus_inv_templ_when_sg {yes,no} [%(sygus_inv_templ_when_sg)s]
sygus_inv_templ {none,pre,post} [%(sygus_inv_templ)s]
sygus_min_grammar {yes,no} [%(sygus_min_grammar)s]
sygus_out {status,status_and_def,sygus_standard} [%(sygus_out)s]
sygus_pbe {yes,no} [%(sygus_pbe)s]
sygus_pbe_multi_fair {yes,no} [%(sygus_pbe_multi_fair)s]
sygus_qe_preproc {yes,no} [%(sygus_qe_preproc)s]
sygus_query_gen_dump_files {none,all,unsolved} [%(sygus_query_gen_dump_files)s]
sygus_query_gen_filter_solved {yes,no} [%(sygus_query_gen_filter_solved)s]
sygus_query_gen {basic,sample_sat,unsat} [%(sygus_query_gen)s]
sygus_rec_fun {yes,no} [%(sygus_rec_fun)s]
sygus_repair_const {yes,no} [%(sygus_repair_const)s]
sygus_rr_synth_accel {yes,no} [%(sygus_rr_synth_accel)s]
sygus_rr_synth_check {yes,no} [%(sygus_rr_synth_check)s]
sygus_rr_synth_filter_cong {yes,no} [%(sygus_rr_synth_filter_cong)s]
sygus_rr_synth_filter_match {yes,no} [%(sygus_rr_synth_filter_match)s]
sygus_rr_synth_filter_nl {yes,no} [%(sygus_rr_synth_filter_nl)s]
sygus_rr_synth_filter_order {yes,no} [%(sygus_rr_synth_filter_order)s]
sygus_rr_synth_rec {yes,no} [%(sygus_rr_synth_rec)s]
sygus_sample_fp_uniform {yes,no} [%(sygus_sample_fp_uniform)s]
sygus_sample_grammar {yes,no} [%(sygus_sample_grammar)s]
sygus_si_abort {yes,no} [%(sygus_si_abort)s]
sygus_si_rcons {none,all_limit,all} [%(sygus_si_rcons)s]
sygus_si {none,use,all} [%(sygus_si)s]
sygus_stream {yes,no} [%(sygus_stream)s]
sygus_unif_cond_independent_no_repeat_sol {yes,no} [%(sygus_unif_cond_independent_no_repeat_sol)s]
sygus_unif_pi {none,complete,cond_enum,cond_enum_igain} [%(sygus_unif_pi)s]
sygus_unif_shuffle_cond {yes,no} [%(sygus_unif_shuffle_cond)s]
symmetry_breaker {yes,no} [%(symmetry_breaker)s]
term_db_cd {yes,no} [%(term_db_cd)s]
term_db_mode {all,relevant} [%(term_db_mode)s]
trigger_active_sel {all,min,max} [%(trigger_active_sel)s]
trigger_sel {min,max,min_s_max,min_s_all,all} [%(trigger_sel)s]
uf_ho_ext {yes,no} [%(uf_ho_ext)s]
uf_lazy_ll {yes,no} [%(uf_lazy_ll)s]
uf_ss_fair {yes,no} [%(uf_ss_fair)s]
uf_ss_fair_monotone {yes,no} [%(uf_ss_fair_monotone)s]
uf_ss {full,no_minimal,none} [%(uf_ss)s]
unconstrained_simp {yes,no} [%(unconstrained_simp)s]
unsat_cores_mode {off,sat_proof,assumptions} [%(unsat_cores_mode)s]
user_pat {use,trust,strict,resort,ignore,interleave} [%(user_pat)s]
user_pool {use,trust,ignore} [%(user_pool)s]
var_elim_quant {yes,no} [%(var_elim_quant)s]
var_ineq_elim_quant {yes,no} [%(var_ineq_elim_quant)s]
"""

CONDITIONS = """
cbqi_all_conflict | cbqi in {yes}
cbqi_eager_check_rd | cbqi in {yes}
cbqi_eager_test | cbqi in {yes}
cbqi_mode | cbqi in {yes}
cbqi_skip_rd | cbqi in {yes}
cbqi_tconstraint | cbqi in {yes}
cbqi_vo_exp | cbqi in {yes}
cegqi_all | cegqi in {yes}
cegqi_bv | cegqi in {yes}
cegqi_bv_concat_inv | cegqi in {yes}
cegqi_bv_ineq | cegqi in {yes}
cegqi_bv_interleave_value | cegqi in {yes}
cegqi_bv_linear | cegqi in {yes}
cegqi_bv_rm_extract | cegqi in {yes}
cegqi_bv_solve_nl | cegqi in {yes}
cegqi_full | cegqi in {yes}
cegqi_inf_int | cegqi in {yes}
cegqi_inf_real | cegqi in {yes}
cegqi_innermost | cegqi in {yes}
cegqi_midpoint | cegqi in {yes}
cegqi_min_bounds | cegqi in {yes}
cegqi_multi_inst | cegqi in {yes}
cegqi_nested_qe | cegqi in {yes}
cegqi_nopt | cegqi in {yes}
cegqi_round_up_lia | cegqi in {yes}
mbqi_interleave | mbqi in {yes}
mbqi_one_inst_per_round | mbqi in {yes}
sygus_add_const_grammar | sygus in {yes}
sygus_arg_relevant | sygus in {yes}
sygus_auto_unfold | sygus in {yes}
sygus_bool_ite_return_const | sygus in {yes}
sygus_core_connective | sygus in {yes}
sygus_crepair_abort | sygus in {yes}
sygus_enum | sygus in {yes}
sygus_inst_scope | sygus in {yes}
sygus_inst_term_sel | sygus in {yes}
sygus_inv_templ_when_sg | sygus in {yes}
sygus_inv_templ | sygus in {yes}
sygus_min_grammar | sygus in {yes}
sygus_out | sygus in {yes}
sygus_pbe | sygus in {yes}
sygus_pbe_multi_fair | sygus in {yes}
sygus_qe_preproc | sygus in {yes}
sygus_query_gen_dump_files | sygus in {yes}
sygus_query_gen_filter_solved | sygus in {yes}
sygus_query_gen | sygus in {yes}
sygus_rec_fun | sygus in {yes}
sygus_repair_const | sygus in {yes}
sygus_rr_synth_accel | sygus in {yes}
sygus_rr_synth_check | sygus in {yes}
sygus_rr_synth_filter_cong | sygus in {yes}
sygus_rr_synth_filter_match | sygus in {yes}
sygus_rr_synth_filter_nl | sygus in {yes}
sygus_rr_synth_filter_order | sygus in {yes}
sygus_rr_synth_rec | sygus in {yes}
sygus_sample_fp_uniform | sygus in {yes}
sygus_sample_grammar | sygus in {yes}
sygus_si_abort | sygus in {yes}
sygus_si_rcons | sygus in {yes}
sygus_si | sygus in {yes}
sygus_stream | sygus in {yes}
sygus_unif_cond_independent_no_repeat_sol | sygus in {yes}
sygus_unif_pi | sygus in {yes}
sygus_unif_shuffle_cond | sygus in {yes}

fmf_bound | finite_model_find in {yes}
fmf_fun | finite_model_find in {yes}
"""

FORBIDDENS = ""

DEFAULTS = {
   'abstract_values': 'no',
   'ackermann': 'no',
   'bv_to_int_use_pow2': 'no',
   'cbqi': 'yes',
   'cbqi_all_conflict': 'no',
   'cbqi_eager_check_rd': 'yes',
   'cbqi_eager_test': 'yes',
   'cbqi_mode': 'prop_eq',
   'cbqi_skip_rd': 'no',
   'cbqi_tconstraint': 'no',
   'cbqi_vo_exp': 'no',
   'cegis_sample': 'none',
   'cegqi': 'no',
   'cegqi_all': 'no',
   'cegqi_bv': 'yes',
   'cegqi_bv_concat_inv': 'yes',
   'cegqi_bv_ineq': 'eq_boundary',
   'cegqi_bv_interleave_value': 'no',
   'cegqi_bv_linear': 'yes',
   'cegqi_bv_rm_extract': 'yes',
   'cegqi_bv_solve_nl': 'no',
   'cegqi_full': 'no',
   'cegqi_inf_int': 'no',
   'cegqi_inf_real': 'no',
   'cegqi_innermost': 'yes',
   'cegqi_midpoint': 'no',
   'cegqi_min_bounds': 'no',
   'cegqi_multi_inst': 'no',
   'cegqi_nested_qe': 'no',
   'cegqi_nopt': 'yes',
   'cegqi_round_up_lia': 'no',
   'check_abducts': 'no',
   'check_interpolants': 'no',
   'check_models': 'no',
   'check_proofs': 'no',
   'check_synth_sol': 'no',
   'check_unsat_cores': 'no',
   'cond_var_split_quant': 'on',
   'conjecture_gen': 'no',
   'cons_exp_triggers': 'no',
   'debug_check_models': 'no',
   'decision': 'internal',
   'deep_restart': 'none',
   'difficulty_mode': 'lemma_literal_all',
   'dt_stc_ind': 'no',
   'dt_var_exp_quant': 'yes',
   'e_matching': 'yes',
   'eager_arith_bv_conv': 'no',
   'early_ite_removal': 'no',
   'elim_taut_quant': 'yes',
   'enum_inst': 'no',
   'enum_inst_interleave': 'no',
   'enum_inst_rd': 'yes',
   'enum_inst_stratify': 'no',
   'enum_inst_sum': 'no',
   'ext_rew_prep': 'off',
   'ext_rewrite_quant': 'no',
   'finite_model_find': 'no',
   'fmf_bound': 'no',
   'fmf_bound_blast': 'no',
   'fmf_bound_lazy': 'no',
   'fmf_fun': 'no',
   'fmf_fun_rlv': 'no',
   'fmf_mbqi': 'fmc',
   'foreign_theory_rewrite': 'no',
   'full_saturate_quant': 'no',
   'global_negate': 'no',
   'ho_elim': 'no',
   'ho_elim_store_ax': 'yes',
   'ho_matching': 'yes',
   'ho_merge_term_db': 'yes',
   'iand_mode': 'value',
   'ieval': 'use',
   'increment_triggers': 'yes',
   'inst_no_entail': 'yes',
   'inst_when': 'full_last_call',
   'int_wf_ind': 'no',
   'interpolants_mode': 'default',
   'ite_dtt_split_quant': 'no',
   'ite_lift_quant': 'simple',
   'ite_simp': 'no',
   'jh_rlv_order': 'no',
   'jh_skolem_rlv': 'assert',
   'jh_skolem': 'first',
   'learned_rewrite': 'no',
   'literal_matching': 'use',
   'macros_quant': 'no',
   'macros_quant_mode': 'ground_uf',
   'mbqi': 'no',
   'mbqi_interleave': 'no',
   'mbqi_one_inst_per_round': 'no',
   'minimal_unsat_cores': 'no',
   'minisat_dump_dimacs': 'no',
   'minisat_simplification': 'all',
   'miniscope_quant': 'conj_and_fv',
   'model_cores': 'none',
   'model_var_elim_uneval': 'yes',
   'multi_trigger_cache': 'no',
   'multi_trigger_linear': 'yes',
   'multi_trigger_priority': 'no',
   'multi_trigger_when_single': 'no',
   'on_repeat_ite_simp': 'no',
   'oracles': 'no',
   'partial_triggers': 'no',
   'pool_inst': 'yes',
   'pre_skolem_quant_nested': 'yes',
   'pre_skolem_quant': 'off',
   'prenex_quant_user': 'no',
   'prenex_quant': 'simple',
   'preregister_mode': 'eager',
   'print_cores_full': 'no',
   'print_inst_full': 'yes',
   'print_inst': 'list',
   'produce_abducts': 'no',
   'produce_assertions': 'yes',
   'produce_assignments': 'no',
   'produce_difficulty': 'no',
   'produce_interpolants': 'no',
   'produce_learned_literals': 'no',
   'produce_models': 'no',
   'produce_proofs': 'no',
   'produce_unsat_assumptions': 'no',
   'produce_unsat_cores': 'no',
   'proof_mode': 'off',
   'purify_triggers': 'no',
   'quant_alpha_equiv': 'yes',
   'quant_dsplit': 'default',
   'quant_fun_wd': 'no',
   'quant_ind': 'no',
   'quant_rep_mode': 'first',
   'register_quant_body_terms': 'no',
   'relational_triggers': 'no',
   'relevant_triggers': 'no',
   'repeat_simp': 'no',
   'simp_ite_compress': 'no',
   'simp_with_care': 'no',
   'simplification_bcp': 'no',
   'simplification': 'batch',
   'solve_bv_as_int': 'off',
   'solve_real_as_int': 'no',
   'sort_inference': 'no',
   'static_learning': 'yes',
   'sygus': 'no',
   'sygus_add_const_grammar': 'yes',
   'sygus_arg_relevant': 'no',
   'sygus_auto_unfold': 'yes',
   'sygus_bool_ite_return_const': 'yes',
   'sygus_core_connective': 'yes',
   'sygus_crepair_abort': 'no',
   'sygus_enum': 'auto',
   'sygus_eval_unfold': 'single_bool',
   'sygus_filter_sol_rev': 'no',
   'sygus_filter_sol': 'none',
   'sygus_grammar_cons': 'simple',
   'sygus_grammar_norm': 'no',
   'sygus_grammar_use_disj': 'yes',
   'sygus_inference': 'no',
   'sygus_inst': 'no',
   'sygus_inst_mode': 'priority_inst',
   'sygus_inst_scope': 'in',
   'sygus_inst_term_sel': 'min',
   'sygus_inv_templ_when_sg': 'no',
   'sygus_inv_templ': 'post',
   'sygus_min_grammar': 'yes',
   'sygus_out': 'sygus_standard',
   'sygus_pbe': 'yes',
   'sygus_pbe_multi_fair': 'no',
   'sygus_qe_preproc': 'no',
   'sygus_query_gen_dump_files': 'none',
   'sygus_query_gen_filter_solved': 'no',
   'sygus_query_gen': 'basic',
   'sygus_rec_fun': 'yes',
   'sygus_repair_const': 'no',
   'sygus_rr_synth_accel': 'no',
   'sygus_rr_synth_check': 'yes',
   'sygus_rr_synth_filter_cong': 'yes',
   'sygus_rr_synth_filter_match': 'yes',
   'sygus_rr_synth_filter_nl': 'no',
   'sygus_rr_synth_filter_order': 'yes',
   'sygus_rr_synth_rec': 'no',
   'sygus_sample_fp_uniform': 'no',
   'sygus_sample_grammar': 'yes',
   'sygus_si_abort': 'no',
   'sygus_si_rcons': 'all',
   'sygus_si': 'none',
   'sygus_stream': 'no',
   'sygus_unif_cond_independent_no_repeat_sol': 'yes',
   'sygus_unif_pi': 'none',
   'sygus_unif_shuffle_cond': 'no',
   'symmetry_breaker': 'yes',
   'term_db_cd': 'yes',
   'term_db_mode': 'all',
   'trigger_active_sel': 'all',
   'trigger_sel': 'min',
   'uf_ho_ext': 'yes',
   'uf_lazy_ll': 'yes',
   'uf_ss_fair': 'yes',
   'uf_ss_fair_monotone': 'no',
   'uf_ss': 'full',
   'unconstrained_simp': 'no',
   'unsat_cores_mode': 'off',
   'user_pat': 'trust',
   'user_pool': 'trust',
   'var_elim_quant': 'yes',
   'var_ineq_elim_quant': 'yes',
}

