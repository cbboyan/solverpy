from ..domain.custom import CustomDomain

TACTICS = [
    "simplify",  # 0
    "solve-eqs",  # 1
    "propagate-values",  # 2
    "elim-uncnstr",  # 3
    "qe",  # 4
    "qe-light",  # 5
    "nnf",  # 6
    "snf",  # 7
    "ctx-simplify",  # 8
    "aig",  # 9
    "sat",  # 10
    #"smt",
]

BOOLS = {
    "simplify": [  # 0
        "elim_and",
        "blast_distinct",
        "push_ite_bv",
        "som",
        "pull_cheap_ite",
        "hoist_mul",
        "local_ctx",
        "flat",
    ],
    "propagate-values": [  # 2
        "push_ite_bv",
    ],
    "qe": [  # 4 
        "eliminate_variables_as_block",
        "qe_nonlinear",
    ],
    "nnf": [  # 6
        "sk_hack",
    ],
    "snf": [  # 7 
        "sk_hack",
    ],
    "ctx-simplify": [  # 8
        "propagate_eq",
    ],
}

BOOL_DOMAIN = ["true", "false"]

DEPTHS = {
    "ctx-simplify": [
        "max-depth",
    ]
}

DEPTH_DOMAIN = [str(2**x) for x in range(12)]


class TacticsDomain(CustomDomain):

    def __init__(self, count, **kwargs):
        CustomDomain.__init__(self, **dict(kwargs, count=count))
        self.n_count = count
        self._count = "t__count"
        self.n_bools, self.has_bools = self.init_args(BOOLS)
        self.n_depths, self.has_depths = self.init_args(DEPTHS)
        self.init_domain()

    def split(self, params):
        cond = lambda x: x.startswith("t__")
        fixed = {x: y for (x, y) in params.items() if not cond(x)}
        params = {x: y for (x, y) in params.items() if cond(x)}
        return (params, fixed)

    def init_args(self, args):
        n_args = max([len(args[arg]) for arg in args])
        has_args = {n + 1: [] for n in range(n_args)}
        for (n, tactic) in enumerate(TACTICS):
            if tactic not in args:
                continue
            for x in range(len(args[tactic])):
                has_args[x + 1].append(str(n))
        return (n_args, has_args)

    def init_domain(self):
        ints = lambda n: list(map(str, range(n)))
        self.add_param(self._count, ints(self.n_count + 1), "0")
        actives = ints(self.n_count + 1)
        for i in range(self.n_count):
            actives.pop(0)
            master = f"t__t{i}"
            self.add_param(master, ints(len(TACTICS)), "0")
            self.add_dep(master, self._count, list(actives))
            self.add_bools(i, master, actives)
            self.add_depths(i, master, actives)

    def add_bools(self, i, master, actives):
        self.add_args(
            i,
            master,
            actives,
            self.n_bools,
            self.has_bools,
            "bool",
            BOOL_DOMAIN,
            "false",
        )

    def add_depths(self, i, master, actives):
        self.add_args(
            i,
            master,
            actives,
            self.n_depths,
            self.has_depths,
            "depth",
            DEPTH_DOMAIN,
            "1024",
        )

    def add_args(
        self,
        i,
        master,
        actives,
        n_args,
        has_args,
        typ,
        domain,
        default,
    ):
        for j in range(n_args):
            name = f"t__t{i}__{typ}{j}"
            self.add_param(name, list(domain), default)
            self.add_dep(name, master, has_args[j + 1])
            self.add_dep(name, self._count, list(actives))


# t__count {0,1,2,3,4} [0]
# t__t1 {0,2,3,4,5,6,7,8,9,10,11,11}
# t__t1__arg1 {on,off} [off]
# t__t1__arg2 {on,off} [off]
# ...
# t__t1__arg8 {on,off} [off]
# t__t1__depth {1,2,4,8,16,32,1024,2048} [1024]

# t__t1__arg1 | t__t1 in {0,2,4,6,7,8}
# t__t1__arg2 | t__t1 in {0,4}
# t__t1__arg3 | t__t1 in {0}
# t__t1__depth | t__t1 in {8}
