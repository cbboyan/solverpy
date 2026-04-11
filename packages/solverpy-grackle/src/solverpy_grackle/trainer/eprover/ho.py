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
        # Defaults match E binary defaults (args() fallbacks).
        # clean() strips params at these values so they produce no CLI flag.
        return {
            "neg_ext": "off",           # no flag
            "pos_ext": "off",           # no flag
            "ext_sup_max_depth": "-1",  # no flag
            "lift_lambdas": "true",     # no flag
            "local_rw": "false",        # no flag
            "fool_unroll": "true",      # no flag
            "inverse_recognition": "false",  # no flag
            "replace_inj_defs": "false",     # no flag
        }
