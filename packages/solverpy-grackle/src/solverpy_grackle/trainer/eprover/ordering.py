from typing import Any
from collections.abc import Mapping

from ..domain.grackle import GrackleDomain, Condition


class OrderingDomain(GrackleDomain):
    """Term ordering: type (LPO4/KBO6), precedence generation, weight generation (KBO only), HO order kind."""

    @property
    def params(self) -> Mapping[str, Any]:
        return {
            "tord": ["LPO4", "KBO6"],
            "tord_prec": ["invfreq", "invfreqconjmax", "invfreqconstmin", "arity",
                          "invarity", "const_max", "freq", "invfreqrank"],
            "tord_weight": ["invfreqrank", "precrank10", "precrank20",
                            "arity", "aritymax0"],
            "tord_const": ["0", "1"],
            "ho_order_kind": ["lfho", "lambda"],
        }

    @property
    def defaults(self) -> dict[str, str]:
        # Defaults match E binary defaults (runner DEFAULTS + args() fallbacks).
        # clean() strips params at these values so they produce no CLI flag.
        return {
            "tord": "LPO4",        # runner DEFAULT
            "tord_prec": "arity",  # runner DEFAULT
            "tord_weight": "arity",# runner DEFAULT (only active for KBO6)
            "tord_const": "0",     # runner DEFAULT (only active for KBO6)
            "ho_order_kind": "lfho",  # no flag (args() fallback)
        }

    @property
    def conditions(self) -> list[Condition]:
        return [
            ("tord_weight", "tord", ["KBO6"]),
            ("tord_const", "tord", ["KBO6"]),
        ]
