from ..domain.grackle import GrackleDomain

class DefaultDomain(GrackleDomain):

   def __init__(self, **kwargs):
      GrackleDomain.__init__(self, **kwargs)
   
   def split(self, params):
      cond = lambda x: x.startswith("a__")
      fixed = {x:y for (x,y) in params.items() if cond(x)}
      params = {x:y for (x,y) in params.items() if not cond(x)}
      return (params, fixed)

   @property
   def params(self):
      return PARAMS

   @property
   def defaults(self):
      return DEFAULTS

   @property 
   def conditions(self):
      return CONDITIONS

D_BOOL = ["set", "clear"]

D_LIMIT = [-1,100,200,500,1000,1500,2000,5000,10000,20000,100000,1000000]

D_FREQ = [0,1,2,3,4,5,6,7,8,9,11,13,17,23,100]

D_MAX = [-1,0,5,10,15,20,30,40,50,100,200,500,1000,1500,2000,5000,99999]

D_WEIGHT = [-1000,-100,-50,-20,-10,-9,-7,-5,-3,-2,-1,0,1,2,3,5,7,9,10,20,23,34,40,50,67,100,200,500,1000,9999,2147483647]

PARAMS = {
   "order":                    "lpo,rpo,kbo", 
   "eq_defs":                  "unfold,fold,pass",
   "inverse_order":            D_BOOL, 
   "expand_relational_defs":   D_BOOL, 
   "predicate_elim":           D_BOOL, 
   "fold_denial_max":          [-1,0,5,10,50,100,1000], 
   "sort_initial_sos":         D_BOOL, 
   "process_initial_sos":      D_BOOL, 
   "sos_limit":                D_LIMIT, 
   "max_given":                D_LIMIT, 
   "max_kept":                 D_LIMIT, 
   "age_part":                 D_FREQ, 
   "weight_part":              D_FREQ, 
   "true_part":                D_FREQ, 
   "false_part":               D_FREQ, 
   "random_part":              D_FREQ, 
   "pick_given_ratio":         D_FREQ,
   #"default_parts":            D_BOOL, 
   #"lightest_first":           D_BOOL, 
   #"breadth_first":            D_BOOL, 
   #"random_given":             D_BOOL, 
   #"input_sos_first":          D_BOOL, 
   "binary_resolution":        D_BOOL, 
   "neg_binary_resolution":    D_BOOL, 
   "ordered_res":              D_BOOL, 
   "check_res_instances":      D_BOOL, 
   "literal_selection":        "max_negative,all_negative,none", 
   "pos_hyper_resolution":     D_BOOL, 
   #"hyper_resolution":         D_BOOL, 
   "neg_hyper_resolution":     D_BOOL, 
   "ur_resolution":            D_BOOL, 
   #"pos_ur_resolution":        D_BOOL, 
   #"neg_ur_resolution":        D_BOOL, 
   "initial_nuclei":           D_BOOL, 
   "ur_nucleus_limit":         [-1,1,10,20,30,40,50], 
   "paramodulation":           D_BOOL, 
   "ordered_para":             D_BOOL, 
   "check_para_instances":     D_BOOL, 
   "para_from_vars":           D_BOOL, 
   "para_lit_limit":           [-1,1,5,10,20,100,9999], 
   "para_units_only":          D_BOOL, 
   #"basic_paramodulation":     D_BOOL, 
   "lex_order_vars":           D_BOOL, 
   "demod_step_limit":         [-1,5,10,100,500,1000,5000,9999], 
   "demod_increase_limit":     [-1,0,10,20,50,100,500,1000,5000,9999], 
   "back_demod":               D_BOOL, 
   "lex_dep_demod":            D_BOOL, 
   "lex_dep_demod_lim":        [-1,1,5,10,11,20,30,40,50,9999], 
   "lex_dep_demod_sane":       D_BOOL, 
   "unit_deletion":            D_BOOL, 
   "cac_redundancy":           D_BOOL, 
   "max_literals":             D_MAX, 
   "max_depth":                D_MAX, 
   "max_vars":                 D_MAX, 
   "max_weight":               D_WEIGHT, 
   "safe_unit_conflict":       D_BOOL, 
   "factor":                   D_BOOL, 
   "new_constants":            [-1,0,1,3,10,20,30,40,50,100,200,500,9999], 
   "back_subsume":             D_BOOL, 
   "backsub_check":            D_LIMIT, 
   "constant_weight":          D_WEIGHT, 
   "sk_constant_weight":       D_WEIGHT, 
   "variable_weight":          D_WEIGHT, 
   "not_weight":               D_WEIGHT, 
   "or_weight":                D_WEIGHT, 
   "prop_atom_weight":         D_WEIGHT, 
   "nest_penalty":             [0,1,2,3,5,7,10,15,9999],
   "depth_penalty":            D_WEIGHT, 
   "var_penalty":              D_WEIGHT, 
   "default_weight":           D_WEIGHT, 
}

DEFAULTS = {
   "order" : "lpo",
   "eq_defs" : "unfold",
   "inverse_order" : "set", 
   "expand_relational_defs" : "clear",
   "predicate_elim" : "set",
   "fold_denial_max" : "0",
   "sort_initial_sos" : "clear",
   "process_initial_sos" : "set", 
   "sos_limit" : "20000",
   "max_given" : "-1", 
   "max_kept" : "-1", 
   "age_part" : "1",
   "weight_part" : "0",
   "true_part" : "4",
   "false_part" : "4",
   "random_part" : "0",
   "pick_given_ratio" : "0",
   #"default_parts" : "set", 
   #"lightest_first" : "clear",
   #"breadth_first" : "clear",
   #"random_given" : "clear",
   #"random_seed" : "0", 
   #"input_sos_first" : "set", 
   "binary_resolution" : "clear",
   "neg_binary_resolution" : "clear",
   "ordered_res" : "set", 
   "check_res_instances" : "clear",
   "literal_selection" : "max_negative",
   "pos_hyper_resolution" : "clear",
   #"hyper_resolution" : "clear",
   "ur_resolution" : "clear",
   "neg_hyper_resolution" : "clear",
   #"pos_ur_resolution" : "clear",
   #"neg_ur_resolution" : "clear",
   "initial_nuclei" : "clear",
   "ur_nucleus_limit" : "-1", 
   "paramodulation" : "clear",
   "ordered_para" : "set",
   "check_para_instances" : "clear",
   "para_from_vars" : "set",
   "para_lit_limit" : "-1",
   "para_units_only" : "clear",
   #"basic_paramodulation" : "clear",
   "lex_order_vars" : "clear",
   "demod_step_limit" : "1000",
   "demod_increase_limit" : "1000",
   "back_demod" : "set", 
   "lex_dep_demod" : "set",
   "lex_dep_demod_lim" : "11",
   "lex_dep_demod_sane" : "set",
   "unit_deletion" : "clear",
   "cac_redundancy" : "set",
   "max_literals" : "-1", 
   "max_depth" : "-1", 
   "max_vars" : "-1", 
   "max_weight" : "100", 
   "safe_unit_conflict" : "clear",
   "factor" : "clear",
   "new_constants" : "0",
   "back_subsume" : "set",
   "backsub_check" : "500", 
   "constant_weight" : "1",
   "sk_constant_weight" : "1",
   "variable_weight" : "1", 
   "not_weight" : "0",
   "or_weight" : "0", 
   "prop_atom_weight" : "1", 
   "nest_penalty" : "0", 
   "depth_penalty" : "0",
   "var_penalty" : "0",
   "default_weight" : "2147483647", 
}

CONDITIONS = [
   ("age_part",     "pick_given_ratio",   [0]), 
   ("weight_part",  "pick_given_ratio",   [0]), 
   ("true_part",    "pick_given_ratio",   [0]), 
   ("false_part",   "pick_given_ratio",   [0]), 
   ("random_part",  "pick_given_ratio",   [0]), 
   ("initial_nuclei",   "ur_resolution", ["set"]),
   ("ur_nucleus_limit", "ur_resolution", ["set"]),
   ("ordered_para",         "paramodulation", ["set"]),
   ("check_para_instances", "paramodulation", ["set"]),
   ("para_from_vars",       "paramodulation", ["set"]),
   ("para_lit_limit",       "paramodulation", ["set"]),
   ("para_units_only",      "paramodulation", ["set"]),
   ("lex_dep_demod",        "back_demod",     ["set"]),
   ("lex_dep_demod_lim",    "lex_dep_demod",  ["set"]),
   ("lex_dep_demod_sane",   "lex_dep_demod",  ["set"]),
]

