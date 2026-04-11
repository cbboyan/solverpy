from typing import Any
from collections.abc import Mapping

from ..domain.grackle import GrackleDomain


class HoDomain(GrackleDomain):
    """HO extension rules, lambda handling, and injectivity options."""

    @property
    def params(self) -> Mapping[str, Any]:
        return {
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
    def defaults(self) -> dict[str, str]:
        return {
            "neg_ext": "all",
            "pos_ext": "all",
            "ext_sup_max_depth": "0",
            "lift_lambdas": "false",
            "local_rw": "true",
            "fool_unroll": "false",
            "inverse_recognition": "false",
            "replace_inj_defs": "false",
        }
