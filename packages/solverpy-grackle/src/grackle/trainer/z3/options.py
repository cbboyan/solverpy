from ..domain.grackle import GrackleDomain


class OptionsDomain(GrackleDomain):

    def __init__(self, **kwargs):
        GrackleDomain.__init__(self, **kwargs)

    @property
    def params(self):
        return PARAMS

    @property
    def defaults(self):
        return DEFAULTS

    @property
    def conditions(self):
        return CONDITIONS

    def split(self, params):
        cond = lambda x: x.startswith("t__")
        params = {x: y for (x, y) in params.items() if not cond(x)}
        fixed = {x: y for (x, y) in params.items() if cond(x)}
        return (params, fixed)

D_BOOL = ["true", "false"]
D_SMALL = [0, 1, 2, 3, 4, 5]
D_MEDIUM = [10, 100, 1000, 10000, 20000]
D_LARGE = [1000, 100000, 100000000, 1000000000]
D_EXTRA = [10000, 10000000, 4294967295]

#D_COST_EXPR   = ["(+ weight generation)", "(+ (* 2 weight) generation)", "(+ weight (* 3 depth))", "generation"]

PARAMS = {
    "nlsat.lazy": [0, 1, 2, 3],
    "nnf.sk_hack": D_BOOL,
    "opt.elim_01": D_BOOL,
    "pi.block_loop_patterns": D_BOOL,
    "pi.decompose_patterns": D_BOOL,
    "pi.enabled": D_BOOL,
    "pi.max_multi_patterns": D_SMALL,
    "pi.pull_quantifiers": D_BOOL,
    "sat.elim_vars": D_BOOL,
    "sat.euf": D_BOOL,
    "sat.smt": D_BOOL,
    "sat.subsumption": D_BOOL,
    "sat.subsumption.limit": D_LARGE,
    "smt.bound_simplifier": D_BOOL,
    "smt.candidate_models": D_BOOL,
    "smt.ematching": D_BOOL,
    "smt.macro_finder": D_BOOL,
    "smt.mbqi": D_BOOL,
    "smt.mbqi.force_template": [5, 10, 20],
    "smt.mbqi.max_cexs": D_SMALL,
    "smt.mbqi.max_cexs_incr": D_SMALL,
    "smt.mbqi.max_iterations": D_MEDIUM,
    "smt.mbqi.trace": D_BOOL,
    "smt.pull_nested_quantifiers": D_BOOL,
    "smt.q.lift_ite": [0, 1, 2],
    "smt.q.lite": D_BOOL,
    #   "smt.qi.cost": D_STRING,
    "smt.qi.eager_threshold": [5, 10, 15, 20],
    "smt.qi.lazy_threshold": [15, 20, 30],
    "smt.qi.max_instances": D_EXTRA,
    "smt.qi.max_multi_patterns": [0] + D_EXTRA,
    "smt.qi.quick_checker": [0, 1, 2],
    "smt.quasi_macros": D_BOOL,
    "smt.refine_inj_axioms": D_BOOL,
    "smt.relevancy": [0, 1, 2],
    "smt.solve_eqs": D_BOOL,
}

DEFAULTS = {
    "nlsat.lazy": "0",
    "nnf.sk_hack": "false",
    "opt.elim_01": "true",
    "pi.block_loop_patterns": "true",
    "pi.decompose_patterns": "true",
    "pi.enabled": "true",
    "pi.max_multi_patterns": "0",
    "pi.pull_quantifiers": "true",
    "sat.elim_vars": "true",
    "sat.euf": "false",
    "sat.smt": "false",
    "sat.subsumption": "true",
    "sat.subsumption.limit": "100000000",
    "smt.bound_simplifier": "true",
    "smt.candidate_models": "false",
    "smt.ematching": "true",
    "smt.macro_finder": "false",
    "smt.mbqi": "true",
    "smt.mbqi.force_template": "10",
    "smt.mbqi.max_cexs": "1",
    "smt.mbqi.max_cexs_incr": "0",
    "smt.mbqi.max_iterations": "1000",
    "smt.mbqi.trace": "false",
    "smt.pull_nested_quantifiers": "false",
    "smt.q.lift_ite": "0",
    "smt.q.lite": "false",
    #   "smt.qi.cost": "(+ weight generation)",
    "smt.qi.eager_threshold": "10",
    "smt.qi.lazy_threshold": "20",
    "smt.qi.max_instances": "4294967295",
    "smt.qi.max_multi_patterns": "0",
    "smt.qi.quick_checker": "0",
    "smt.quasi_macros": "false",
    "smt.refine_inj_axioms": "true",
    "smt.relevancy": "2",
    "smt.solve_eqs": "true",
}

CONDITIONS = [
    ("sat.subsumption.limit", "sat.subsumption", ["true"]),
    ("smt.mbqi.force_template", "smt.mbqi", ["true"]),
    ("smt.mbqi.max_cexs", "smt.mbqi", ["true"]),
    ("smt.mbqi.max_cexs_incr", "smt.mbqi", ["true"]),
    ("smt.mbqi.max_iterations", "smt.mbqi", ["true"]),
    ("smt.mbqi.trace", "smt.mbqi", ["true"]),
]
