
REPLACE = {
   "selection" : "-",
   "age_weight_ratio" : ":",
}

PARAMS = """
age_weight_ratio {__1_1,__1_2,__2_1,__1_4,__4_1,__1_10,__1_1024,__1_12,__1_128,__1_14,__1_16,__1_20,__1_24,__1_28,__1_3,__1_32,__1_40,__1_5,__1_50,__1_6,__1_64,__1_7,__1_8,__2_3,__3_1,__3_2,__5_1,__5_4,__8_1} [%(age_weight_ratio)s]
age_weight_ratio_shape {constant,decay,converge} [%(age_weight_ratio_shape)s]
age_weight_ratio_shape_frequency {100,1,128,16,2,256,32,4,512,64,8} [%(age_weight_ratio_shape_frequency)s]
avatar {off,on} [%(avatar)s]
avatar_add_complementary {ground,none} [%(avatar_add_complementary)s]
avatar_congruence_closure {model,off,on} [%(avatar_congruence_closure)s]
avatar_fast_restart {off,on} [%(avatar_fast_restart)s]
avatar_flush_period {0,1000,10000,100000,4000,40000} [%(avatar_flush_period)s]
avatar_flush_quotient {1.0,1.1,1.2,1.4,1.5,2.0} [%(avatar_flush_quotient)s]
avatar_minimize_model {off,sco,all} [%(avatar_minimize_model)s]
avatar_nonsplittable_components {all,all_dependent,known,none} [%(avatar_nonsplittable_components)s]
backward_demodulation {all,off,preordered} [%(backward_demodulation)s]
backward_subsumption {off,on,unit_only} [%(backward_subsumption)s]
backward_subsumption_resolution {off,on,unit_only} [%(backward_subsumption_resolution)s]
binary_resolution {off,on} [%(binary_resolution)s]
cc_unsat_cores {first,small_ones,all} [%(cc_unsat_cores)s]
condensation {fast,off,on} [%(condensation)s]
extensionality_resolution {filter,known,off} [%(extensionality_resolution)s]
forward_subsumption_resolution {off,on} [%(forward_subsumption_resolution)s]
function_definition_elimination {all,none,unused} [%(function_definition_elimination)s]
general_splitting {input_only,off} [%(general_splitting)s]
global_subsumption {off,on} [%(global_subsumption)s]
global_subsumption_explicit_minim {off,on,randomized} [%(global_subsumption_explicit_minim)s]
inner_rewriting {off,on} [%(inner_rewriting)s]
literal_comparison_mode {predicate,reverse,standard} [%(literal_comparison_mode)s]
literal_maximality_aftercheck {off,on} [%(literal_maximality_aftercheck)s]
lrs_weight_limit_only {off,on} [%(lrs_weight_limit_only)s]
naming {8,0,1024,16,2,32,4,6,64} [%(naming)s]
newcnf {off,on} [%(newcnf)s]
nongoal_weight_coefficient {1,1.1,1.2,1.3,1.5,1.7,10,2,2.5,3,4,5} [%(nongoal_weight_coefficient)s]
nonliterals_in_clause_weight {off,on} [%(nonliterals_in_clause_weight)s]
sat_solver {minisat} [%(sat_solver)s]
saturation_algorithm {discount,fmb,inst_gen,lrs,otter} [%(saturation_algorithm)s]
selection {_1,1,_10,10,1002,1003,1004,1010,1011,_11,11,_2,2,_3,3,_4,4} [%(selection)s]
sine_depth {0,1,10,2,3,4,5,7} [%(sine_depth)s]
sine_selection {axioms,included,off} [%(sine_selection)s]
sine_to_age {off,on} [%(sine_to_age)s]
sine_tolerance {1,1.2,1.5,2.0,3.0,5.0} [%(sine_tolerance)s]
sos {all,off,on,theory} [%(sos)s]
symbol_precedence {arity,occurrence,reverse_arity,frequency,reverse_frequency} [%(symbol_precedence)s]
term_ordering {kbo,lpo} [%(term_ordering)s]
unit_resulting_resolution {ec_only,off,on} [%(unit_resulting_resolution)s]
unused_predicate_definition_removal {off,on} [%(unused_predicate_definition_removal)s]
"""

CONDITIONS = ""

FORBIDDENS = """
{age_weight_ratio=__1_2,saturation_algorithm=inst_gen}
{age_weight_ratio=__2_1,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_4,saturation_algorithm=inst_gen}
{age_weight_ratio=__4_1,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_10,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_1024,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_12,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_128,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_14,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_16,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_20,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_24,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_28,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_3,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_32,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_40,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_5,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_50,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_6,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_64,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_7,saturation_algorithm=inst_gen}
{age_weight_ratio=__1_8,saturation_algorithm=inst_gen}
{age_weight_ratio=__2_3,saturation_algorithm=inst_gen}
{age_weight_ratio=__3_1,saturation_algorithm=inst_gen}
{age_weight_ratio=__3_2,saturation_algorithm=inst_gen}
{age_weight_ratio=__5_1,saturation_algorithm=inst_gen}
{age_weight_ratio=__5_4,saturation_algorithm=inst_gen}
{age_weight_ratio=__8_1,saturation_algorithm=inst_gen}
{backward_demodulation=off,saturation_algorithm=inst_gen}
{backward_demodulation=preordered,saturation_algorithm=inst_gen}
{backward_subsumption=on,saturation_algorithm=inst_gen}
{backward_subsumption=unit_only,saturation_algorithm=inst_gen}
{backward_subsumption_resolution=on,saturation_algorithm=inst_gen}
{backward_subsumption_resolution=unit_only,saturation_algorithm=inst_gen}
{condensation=fast,saturation_algorithm=inst_gen}
{condensation=on,saturation_algorithm=inst_gen}
{forward_subsumption_resolution=off,saturation_algorithm=inst_gen}
{selection=_1,saturation_algorithm=inst_gen}
{selection=1,saturation_algorithm=inst_gen}
{selection=_10,saturation_algorithm=inst_gen}
{selection=1002,saturation_algorithm=inst_gen}
{selection=1003,saturation_algorithm=inst_gen}
{selection=1004,saturation_algorithm=inst_gen}
{selection=1010,saturation_algorithm=inst_gen}
{selection=1011,saturation_algorithm=inst_gen}
{selection=_11,saturation_algorithm=inst_gen}
{selection=11,saturation_algorithm=inst_gen}
{selection=_2,saturation_algorithm=inst_gen}
{selection=2,saturation_algorithm=inst_gen}
{selection=_3,saturation_algorithm=inst_gen}
{selection=3,saturation_algorithm=inst_gen}
{selection=_4,saturation_algorithm=inst_gen}
{selection=4,saturation_algorithm=inst_gen}
{avatar_congruence_closure=model,avatar_minimize_model=sco}
{saturation_algorithm=inst_gen,avatar=on}
{selection=1002,saturation_algorithm=inst_gen}
{selection=1003,saturation_algorithm=inst_gen}
{selection=1004,saturation_algorithm=inst_gen}
{selection=1010,saturation_algorithm=inst_gen}
{selection=1011,saturation_algorithm=inst_gen}
{avatar_add_complementary=none,avatar=off}
{avatar_congruence_closure=model,avatar=off}
{avatar_congruence_closure=on,avatar=off}
{avatar_fast_restart=on,avatar=off}
{avatar_flush_period=1000,avatar=off}
{avatar_flush_period=10000,avatar=off}
{avatar_flush_period=100000,avatar=off}
{avatar_flush_period=4000,avatar=off}
{avatar_flush_period=40000,avatar=off}
{avatar_flush_quotient=1.0,avatar=off}
{avatar_flush_quotient=1.1,avatar=off}
{avatar_flush_quotient=1.2,avatar=off}
{avatar_flush_quotient=1.4,avatar=off}
{avatar_flush_quotient=2.0,avatar=off}
{avatar_minimize_model=off,avatar=off}
{avatar_minimize_model=sco,avatar=off}
{avatar_nonsplittable_components=all,avatar=off}
{avatar_nonsplittable_components=all_dependent,avatar=off}
{avatar_nonsplittable_components=none,avatar=off}
{nonliterals_in_clause_weight=on,avatar=off}
{global_subsumption_explicit_minim=off,global_subsumption=off}
{global_subsumption_explicit_minim=on,global_subsumption=off}
{sine_selection=axioms,saturation_algorithm=fmb}
{sine_selection=included,saturation_algorithm=fmb}
{binary_resolution=off,unit_resulting_resolution=off}
{cc_unsat_cores=first,avatar_congruence_closure=off}
{cc_unsat_cores=small_ones,avatar_congruence_closure=off}
{sine_tolerance=1.2,sine_selection=off}
{sine_tolerance=1.5,sine_selection=off}
{sine_tolerance=2.0,sine_selection=off}
{sine_tolerance=3.0,sine_selection=off}
{sine_tolerance=5.0,sine_selection=off}
{sine_depth=1,sine_selection=off}
{sine_depth=10,sine_selection=off}
{sine_depth=2,sine_selection=off}
{sine_depth=3,sine_selection=off}
{sine_depth=4,sine_selection=off}
{sine_depth=5,sine_selection=off}
{sine_depth=7,sine_selection=off}
"""


DEFAULTS = {
   "age_weight_ratio": "__1_1",
   "age_weight_ratio_shape": "constant",
   "age_weight_ratio_shape_frequency": "100",
   "avatar": "on",
   "avatar_add_complementary": "ground",
   "avatar_congruence_closure": "off",
   "avatar_fast_restart": "off",
   "avatar_flush_period": "0",
   "avatar_flush_quotient": "1.5",
   "avatar_minimize_model": "all",
   "avatar_nonsplittable_components": "known",
   "backward_demodulation": "all",
   "backward_subsumption": "off",
   "backward_subsumption_resolution": "off",
   "binary_resolution": "on",
   "cc_unsat_cores": "all",
   "condensation": "off",
   "extensionality_resolution": "off",
   "forward_subsumption_resolution": "on",
   "function_definition_elimination": "all",
   "general_splitting": "off",
   "global_subsumption": "off",
   "global_subsumption_explicit_minim": "randomized",
   "inner_rewriting": "off",
   "literal_comparison_mode": "standard",
   "literal_maximality_aftercheck": "off",
   "lrs_weight_limit_only": "off",
   "naming": "8",
   "newcnf": "off",
   "nongoal_weight_coefficient": "1",
   "nonliterals_in_clause_weight": "off",
   "sat_solver": "minisat",
   "saturation_algorithm": "lrs",
   "selection": "10",
   "sine_depth": "0",
   "sine_selection": "off",
   "sine_to_age": "off",
   "sine_tolerance": "1",
   "sos": "off",
   "symbol_precedence": "arity",
   "term_ordering": "kbo",
   "unit_resulting_resolution": "off",
   "unused_predicate_definition_removal": "on",
}

