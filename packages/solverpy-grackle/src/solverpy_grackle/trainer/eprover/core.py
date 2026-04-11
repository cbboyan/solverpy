from typing import Any
from collections.abc import Mapping

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
    def params(self) -> Mapping[str, Any]:
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
        }

    @property
    def defaults(self) -> dict[str, str]:
        # Defaults match E binary defaults (runner DEFAULTS + args() fallbacks).
        # clean() strips params at these values; convert() fills them back in.
        return {
            "sel": "SelectMaxLComplexAvoidPosPred",  # runner DEFAULT
            "simparamod": "none",   # no flag
            "der": "none",          # no flag
            "forwardcntxtsr": "0",  # no flag
            "fwdemod": "2",         # direct sentinel: no flag
            "condense": "0",        # no flag
            "presat": "0",          # no flag
            "prefer": "0",          # no flag
            "splaggr": "0",         # no flag
            "srd": "0",             # no flag
            "splcl": "0",           # direct sentinel: no flag
            "defcnf": "24",         # runner DEFAULT
            "strong_rw_inst": "0",  # no flag (args() fallback)
            "no_eq_unfolding": "0", # no flag (args() fallback)
            "sos_input_types": "0", # no flag (args() fallback)
            "satcheck": "none",     # no flag (args() fallback)
        }
