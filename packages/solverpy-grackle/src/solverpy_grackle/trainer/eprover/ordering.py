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
        return {
            "tord": "KBO6",
            "tord_prec": "invfreq",
            "tord_weight": "precrank10",
            "tord_const": "1",
            "ho_order_kind": "lfho",
        }

    @property
    def conditions(self) -> list[Condition]:
        return [
            ("tord_weight", "tord", ["KBO6"]),
            ("tord_const", "tord", ["KBO6"]),
        ]
