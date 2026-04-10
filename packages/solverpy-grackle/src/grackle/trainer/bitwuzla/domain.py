from ..domain.grackle import GrackleDomain, _parse_params, _parse_conditions, _parse_forbiddens


class BitwuzlaDomain(GrackleDomain):

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
ackermannize {0,1} [%(ackermannize)s]
beta_reduce {none,fun,all} [%(beta_reduce)s]
eliminate_ites {0,1} [%(eliminate_ites)s]
eliminate_slices {0,1} [%(eliminate_slices)s]
engine {aigprop,fun,prop,sls,quant} [%(engine)s]
extract_lambdas {0,1} [%(extract_lambdas)s]
fun_dual_prop {0,1} [%(fun_dual_prop)s]
fun_dual_prop_qsort {just,asc,desc} [%(fun_dual_prop_qsort)s]
fun_eager_lemmas {none,conf,all} [%(fun_eager_lemmas)s]
fun_just {0,1} [%(fun_just)s]
fun_just_heuristic {left,applies,depth} [%(fun_just_heuristic)s]
fun_lazy_synthesize {0,1} [%(fun_lazy_synthesize)s]
fun_preprop {0,1} [%(fun_preprop)s]
fun_presls {0,1} [%(fun_presls)s]
fun_store_lambdas {0,1} [%(fun_store_lambdas)s]
merge_lambdas {0,1} [%(merge_lambdas)s]
nondestr_subst {0,1} [%(nondestr_subst)s]
normalize {0,1} [%(normalize)s]
normalize_add {0,1} [%(normalize_add)s]
rewrite_level {0,1,2,3} [%(rewrite_level)s]
rw_extract_arith {0,1} [%(rw_extract_arith)s]
rw_slt {0,1} [%(rw_slt)s]
sat_engine {cadical,cms,lingeling,picosat,kissat} [%(sat_engine)s]
simplify_constraints {0,1} [%(simplify_constraints)s]
simp_norm_adds {0,1} [%(simp_norm_adds)s]
skeleton_preproc {0,1} [%(skeleton_preproc)s]
sort_aig {0,1} [%(sort_aig)s]
sort_aigvec {0,1} [%(sort_aigvec)s]
sort_exp {0,1} [%(sort_exp)s]
ucopt {0,1} [%(ucopt)s]
var_subst {0,1} [%(var_subst)s]
# new ones:
declsort_bv_width {0,1,2,8,16} [%(declsort_bv_width)s]
prop_const_bits {0,1} [%(prop_const_bits)s]
prop_infer_ineq_bounds {0,1} [%(prop_infer_ineq_bounds)s]
prop_nprops {0,2000,10000,100000} [%(prop_nprops)s]
prop_nupdates {0,90000,2000000,9000000} [%(prop_nupdates)s]
prop_prob_rand_input {0,10,100} [%(prop_prob_rand_input)s]
prop_sext {0,1} [%(prop_sext)s]
prop_use_inv_lt_concat {0,1} [%(prop_use_inv_lt_concat)s]
"""

CONDITIONS = """
fun_dual_prop_qsort | fun_dual_prop in {1}
fun_just_heuristic | fun_just in {1}
"""

FORBIDDENS = """
{fun_dual_prop=1,fun_just=1}
{fun_dual_prop=1,nondestr_subst=1}
"""

DEFAULTS = {
   "ackermannize": "0",
   "aigprop_nprops": "0",
   "aigprop_use_bandit": "0",
   "aigprop_use_restarts": "0",
   "auto_cleanup": "0",
   "auto_cleanup_internal": "0",
   "beta_reduce": "none",
   "check_failed_assumptions": "1",
   "check_model": "1",
   "check_unconstrained": "1",
   "declsort_bv_width": "0",
   "dump_aiger_merge": "0",
   "dump_dimacs": "0",
   "eliminate_ites": "0",
   "eliminate_slices": "1",
   "engine": "fun",
   "exit_codes": "1",
   "extract_lambdas": "1",
   "fun_dual_prop": "0",
   "fun_dual_prop_qsort": "just",
   "fun_eager_lemmas": "conf",
   "fun_just": "0",
   "fun_just_heuristic": "applies",
   "fun_lazy_synthesize": "0",
   "fun_preprop": "0",
   "fun_presls": "0",
   "fun_store_lambdas": "0",
   "incremental": "0",
   "ls_share_sat": "0",
   "merge_lambdas": "1",
   "model_gen": "0",
   "nondestr_subst": "0",
   "normalize": "1",
   "normalize_add": "1",
   "output_format": "none",
   "output_number_format": "bin",
   "parse_interactive": "1",
   "pretty_print": "1",
   "prop_ashr": "0",
   "prop_const_bits": "1",
   "prop_const_domains": "0",
   "prop_entailed": "off",
   "prop_flip_cond_const_delta": "100",
   "prop_flip_cond_const_npathsel": "500",
   "prop_infer_ineq_bounds": "0",
   "prop_no_move_on_conflict": "0",
   "prop_nprops": "0",
   "prop_nupdates": "0",
   "prop_path_sel": "essential",
   "prop_prob_and_flip": "0",
   "prop_prob_eq_flip": "0",
   "prop_prob_fallback_rand_value": "0",
   "prop_prob_flip_cond": "100",
   "prop_prob_flip_cond_const": "100",
   "prop_prob_rand_input": "0",
   "prop_prob_slice_flip": "0",
   "prop_prob_slice_keep_dc": "500",
   "prop_prob_use_inv_value": "990",
   "prop_sext": "0",
   "prop_skip_no_progress": "0",
   "prop_use_bandit": "0",
   "prop_use_inv_lt_concat": "0",
   "prop_use_restarts": "0",
   "prop_xor": "0",
   "quant_cer": "1",
   "quant_der": "1",
   "quant_dual": "1",
   "quant_fixsynth": "1",
   "quant_ms": "1",
   "quant_synth": "elmr",
   "quant_synthcomplete": "1",
   "quant_synthlimit": "10000",
   "quant_synthqi": "1",
   "rewrite_level": "3",
   "rw_extract_arith": "0",
   "rw_slt": "0",
   "sat_engine": "cadical",
   "sat_engine_cadical_freeze": "0",
   "sat_engine_lgl_fork": "1",
   "sat_engine_n_threads": "1",
   "simp_norm_adds": "0",
   "simplify_constraints": "1",
   "skeleton_preproc": "1",
   "sls_just": "0",
   "sls_move_gw": "0",
   "sls_move_inc_move_test": "0",
   "sls_move_prop": "0",
   "sls_move_prop_force_rw": "0",
   "sls_move_prop_n_prop": "1",
   "sls_move_prop_n_sls": "1",
   "sls_move_rand_all": "0",
   "sls_move_rand_range": "0",
   "sls_move_rand_walk": "0",
   "sls_move_range": "0",
   "sls_move_segment": "0",
   "sls_nflips": "0",
   "sls_prob_move_rand_walk": "100",
   "sls_strategy": "best",
   "sls_use_bandit": "1",
   "sls_use_restarts": "1",
   "sort_aig": "1",
   "sort_aigvec": "1",
   "sort_exp": "1",
   "ucopt": "0",
   "unsat_cores": "0",
   "var_subst": "1",
   "smt_comp_mode": "0",
}

