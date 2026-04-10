from ..domain.grackle import GrackleDomain

class DefaultDomain(GrackleDomain):

   def __init__(self, **kwargs):
      GrackleDomain.__init__(self, **kwargs)

   @property
   def params(self):
      return DOMAINS

   @property
   def defaults(self):
      return DEFAULTS

   @property
   def conditions(self):
      return CONDITIONS


D_BOOL = ["true", "false"]

D_PROB = [0, 10, 50, 500, 950, 990, 1000]

D_STEPS = [0, 10, 100, 1000, 9999999]

D_BITS = [16, 32 ,33]

D_REFS = [10, 100, 1000]

DOMAINS = dict(
   relevant_terms=D_BOOL,
   bv_solver="preprop,prop,bitblast",
   rewrite_level="0,1,2",
   sat_solver="kissat,cms,cadical",
   prop_const_bits=D_BOOL,
   prop_ineq_bounds=D_BOOL,
   prop_nprops=D_STEPS, # <n> [0],
   prop_nupdates=D_STEPS, # <n> [0],
   prop_opt_lt_concat_sext=D_BOOL,
   prop_path_sel="random,essential",
   prop_prob_pick_rand_input=D_PROB, # <n> [10] {0..1000} "<n> / 1000 = probability",
   prop_prob_pick_inv_value=D_PROB,  # <n> [990] {0..1000},
   prop_sext=D_BOOL,
   prop_normalize=D_BOOL,
   abstraction=D_BOOL,
   abstraction_bv_size=D_BITS, # <n> [32] {0..},
   abstraction_eager_refine=D_BOOL,
   abstraction_value_limit=[1,2,4,8],   #<n> [8] {0..bv-size} "bv-size / <n>",
   abstraction_value_only=D_BOOL,
   abstraction_assert=D_BOOL,
   abstraction_assert_refs=D_REFS, #<n> [100] {1..},
   abstraction_initial_lemmas=D_BOOL,
   abstraction_inc_bitblast=D_BOOL,
   abstraction_bvadd=D_BOOL,
   abstraction_bvmul=D_BOOL,
   abstraction_bvudiv=D_BOOL,
   abstraction_bvurem=D_BOOL,
   abstraction_eq=D_BOOL,
   abstraction_ite=D_BOOL,
   preprocess=D_BOOL,
   pp_contr_ands=D_BOOL,
   pp_elim_extracts=D_BOOL,
   pp_elim_bvudiv=D_BOOL,
   pp_embedded=D_BOOL,
   pp_flatten_and=D_BOOL,
   pp_normalize=D_BOOL,
   pp_normalize_share_aware=D_BOOL,
   pp_skeleton_preproc=D_BOOL,
   pp_variable_subst=D_BOOL,
   pp_variable_subst_norm_eq=D_BOOL,
   pp_variable_subst_norm_diseq=D_BOOL,
   pp_variable_subst_norm_bv_ineq=D_BOOL,
)

DEFAULTS = dict(
   relevant_terms="false",
   bv_solver="bitblast",
   rewrite_level="2",
   sat_solver="cadical",
   prop_const_bits="true",
   prop_ineq_bounds="true",
   prop_nprops="0",
   prop_nupdates="0",
   prop_opt_lt_concat_sext="false",
   prop_path_sel="essential",
   prop_prob_pick_rand_input="10",
   prop_prob_pick_inv_value="990",
   prop_sext="true",
   prop_normalize="false",
   abstraction="false",
   abstraction_bv_size="32",
   abstraction_eager_refine="false",
   abstraction_value_limit="8",
   abstraction_value_only="false",
   abstraction_assert="false",
   abstraction_assert_refs="100",
   abstraction_initial_lemmas="false",
   abstraction_inc_bitblast="false",
   abstraction_bvadd="false",
   abstraction_bvmul="true",
   abstraction_bvudiv="true",
   abstraction_bvurem="true",
   abstraction_eq="false",
   abstraction_ite="false",
   preprocess="true",
   pp_contr_ands="false",
   pp_elim_extracts="false",
   pp_elim_bvudiv="false",
   pp_embedded="true",
   pp_flatten_and="true",
   pp_normalize="true",
   pp_normalize_share_aware="true",
   pp_skeleton_preproc="true",
   pp_variable_subst="true",
   pp_variable_subst_norm_eq="true",
   pp_variable_subst_norm_diseq="false",
   pp_variable_subst_norm_bv_ineq="false",
)

CONDITIONS = [
   ("abstraction_bv_size",        "abstraction", ["true"]),
   ("abstraction_eager_refine",   "abstraction", ["true"]),
   ("abstraction_value_limit",    "abstraction", ["true"]),
   ("abstraction_value_only",     "abstraction", ["true"]),
   ("abstraction_assert",         "abstraction", ["true"]),
   ("abstraction_initial_lemmas", "abstraction", ["true"]),
   ("abstraction_inc_bitblast",   "abstraction", ["true"]),
   ("abstraction_bvadd",          "abstraction", ["true"]),
   ("abstraction_bvmul",          "abstraction", ["true"]),
   ("abstraction_bvudiv",         "abstraction", ["true"]),
   ("abstraction_bvurem",         "abstraction", ["true"]),
   ("abstraction_eq",             "abstraction", ["true"]),
   ("abstraction_ite",            "abstraction", ["true"]),
   #
   ("abstraction_assert_refs",    "abstraction_assert", ["true"]),
   #
   ("pp_contr_ands",       "preprocess", ["true"]),
   ("pp_elim_extracts",    "preprocess", ["true"]),
   ("pp_elim_bvudiv",      "preprocess", ["true"]),
   ("pp_embedded",         "preprocess", ["true"]),
   ("pp_flatten_and",      "preprocess", ["true"]),
   ("pp_normalize",        "preprocess", ["true"]),
   ("pp_skeleton_preproc", "preprocess", ["true"]),
   ("pp_variable_subst",   "preprocess", ["true"]),
   #
   ("pp_normalize_share_aware", "pp_normalize", ["true"]),
   #
   ("pp_variable_subst_norm_eq",      "pp_variable_subst", ["true"]),
   ("pp_variable_subst_norm_diseq",   "pp_variable_subst", ["true"]),
   ("pp_variable_subst_norm_bv_ineq", "pp_variable_subst", ["true"]),
]

