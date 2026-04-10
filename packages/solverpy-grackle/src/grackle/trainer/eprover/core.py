from ..domain.grackle import GrackleDomain


class CoreDomain(GrackleDomain):
    """Core proof-search options: literal selection, inference control, simplification,
    HO extension rules and lambda handling, SAT checking."""

    _SEL = [
        "SelectMaxLComplexAvoidAppVar",       # best for HO (nb7 family)
        "SelectComplexExceptUniqMaxHorn",     # FO-compatible (pre_casc, post_as_ho1)
        "PSelectComplexExceptUniqMaxHorn",    # HO-specific (new_ho_11, sh6)
        "SelectMaxLComplexAPPNTNp",           # HO (sh5, sh5l)
        "SelectMaxLComplexAvoidPosPred",      # FO classic (mzr05, bls)
        "SelectNewComplexAHP",                # FO (bls0222)
        "SelectComplexG",                     # FO (mzr01, mzr10)
        "SelectCQIPrecWNTNp",                 # FO (eprover66)
        "SelectNoLiterals",                   # baseline
    ]

    @property
    def params(self):
        return {
            # Literal selection
            "sel": self._SEL,
            # Paramodulation
            "simparamod": ["none", "normal", "oriented"],
            # Destructive ER
            "der": ["none", "std", "strong", "agg", "stragg"],
            # Simplification
            "forwardcntxtsr": ["0", "1"],
            "fwdemod": ["0", "1", "2"],
            "condense": ["0", "1"],
            "presat": ["0", "1"],
            "prefer": ["0", "1"],
            # Splitting
            "splaggr": ["0", "1"],
            "srd": ["0", "1"],
            "splcl": ["0", "4", "7"],
            # Preprocessing
            "defcnf": ["none", "0", "3", "4", "6", "8", "12", "24"],
            "strong_rw_inst": ["0", "1"],
            "no_eq_unfolding": ["0", "1"],
            "sos_input_types": ["0", "1"],
            # SAT checking
            "satcheck": ["none", "ConjMinMinFreq"],
            # HO extension rules
            "neg_ext": ["off", "all"],
            "pos_ext": ["off", "all"],
            "ext_sup_max_depth": ["-1", "0", "1"],
            # HO lambda handling
            "lift_lambdas": ["true", "false"],
            "local_rw": ["false", "true"],
            "fool_unroll": ["true", "false"],
            # HO injectivity
            "inverse_recognition": ["false", "true"],
            "replace_inj_defs": ["false", "true"],
        }

    @property
    def defaults(self):
        # Defaults match the nb7 / new_bool_7 strategy profile
        return {
            "sel": "SelectMaxLComplexAvoidAppVar",
            "simparamod": "normal",
            "der": "stragg",
            "forwardcntxtsr": "1",
            "fwdemod": "1",
            "condense": "1",
            "presat": "1",
            "prefer": "0",
            "splaggr": "0",
            "srd": "0",
            "splcl": "0",
            "defcnf": "4",
            "strong_rw_inst": "1",
            "no_eq_unfolding": "1",
            "sos_input_types": "1",
            "satcheck": "ConjMinMinFreq",
            "neg_ext": "all",
            "pos_ext": "all",
            "ext_sup_max_depth": "0",
            "lift_lambdas": "false",
            "local_rw": "true",
            "fool_unroll": "false",
            "inverse_recognition": "false",
            "replace_inj_defs": "false",
        }
