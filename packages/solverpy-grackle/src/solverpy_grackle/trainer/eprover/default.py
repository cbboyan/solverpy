from ..domain.multi import MultiDomain
from .core import CoreDomain
from .ordering import OrderingDomain
from .heuristic import HeuristicDomain


class DefaultDomain(MultiDomain):
    """Default E prover domain: core + ordering + heuristic (without SinE)."""

    def __init__(self):
        MultiDomain.__init__(self, domains=[
            CoreDomain(),
            OrderingDomain(),
            HeuristicDomain(),
        ])
