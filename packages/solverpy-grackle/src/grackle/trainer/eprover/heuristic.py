from ..domain.grackle import GrackleDomain


# 20 predefined (freq, CEF) pairs for heuristic slot selection.
# Indexed 0-19; EproverRunner maps indices back to these strings.
# Sources: nb7/new_bool (0-4), pre_casc/post_as_ho (5-7), HO-specific sh3/new_bool_8/new_ho (8-10),
#          mzr02 similarity weights / yan (11-17), mzr01/bls0f17 (18-19).
HEURISTIC_CEFS = [
    # 0-4: nb7 / new_bool family
    (2, "ConjectureRelativeSymbolWeight(PreferGround,0.5,100,100,100,100,1.5,1.5,1)"),
    (6, "ConjectureRelativeSymbolWeight(ByDerivationDepth,0.1,100,100,100,100,1.5,1.5,1.5)"),
    (1, "FIFOWeight(PreferProcessed)"),
    (1, "ConjectureRelativeSymbolWeight(PreferNonGoals,0.5,100,100,100,100,1.5,1.5,1)"),
    (2, "Refinedweight(PreferGoals,3,2,2,1.5,2)"),
    # 5-7: pre_casc / post_as_ho / eprover66 family
    (1, "ConjectureRelativeSymbolWeight(SimulateSOS,0.5,100,100,100,100,1.5,1.5,1)"),
    (4, "ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5)"),
    (4, "Refinedweight(SimulateSOS,3,2,2,1.5,2)"),
    # 8-10: HO-specific (sh3 / new_bool_8 / new_ho_11)
    (4, "ConjectureRelativeSymbolWeight(PreferFO,0.1,100,100,100,100,1.5,1.5,1.5)"),
    (1, "ConjectureRelativeSymbolWeight(PreferHOSteps,0.5,100,100,100,100,1.5,1.5,1)"),
    (1, "ConjectureRelativeSymbolWeight(PreferNonGoals,3,9999,4,3,5,4,4,2.5)"),
    # 11-17: mzr02 family (yan's similarity / prefix weight functions)
    (1, "ConjectureTermPrefixWeight(DeferSOS,1,3,0.1,5,0,0.1,1,4)"),
    (1, "ConjectureTermPrefixWeight(PreferNonGoals,1,3,100,9999.9,0,9999.9,3,5)"),
    (1, "StaggeredWeight(DeferSOS,1)"),
    (2, "StaggeredWeight(DeferSOS,2)"),
    (1, "SymbolTypeweight(DeferSOS,18,7,-2,5,9999.9,2,1.5)"),
    (2, "Clauseweight(PreferWatchlist,20,9999,4)"),
    (2, "ConjectureSymbolWeight(DeferSOS,9999,20,50,-1,50,3,3,0.5)"),
    # 18-19: mzr01 / bls0f17 family
    (1, "RelevanceLevelWeight2(ConstPrio,1,0,2,2,7,-1,2,0,0.2,9999.9,9999.9)"),
    (5, "Clauseweight(PreferUnitGroundGoals,7,9999,5)"),
]

N_CEFS = len(HEURISTIC_CEFS)  # 20


class HeuristicDomain(GrackleDomain):
    """Clause selection heuristic: up to 4 slots, each picking one of N_CEFS predefined (freq, CEF) pairs.
    EproverRunner always appends 1*FIFOWeight(ConstPrio) as the final CEF for completeness."""

    @property
    def params(self):
        indices = [str(i) for i in range(N_CEFS)]
        return {
            "slots": ["1", "2", "3", "4"],
            "heur0": indices,
            "heur1": indices,
            "heur2": indices,
            "heur3": indices,
        }

    @property
    def defaults(self):
        return {
            "slots": "4",
            "heur0": "0",   # 2*CRSW(PreferGround,...)
            "heur1": "1",   # 6*CRSW(ByDerivationDepth,...)
            "heur2": "2",   # 1*FIFOWeight(PreferProcessed)
            "heur3": "3",   # 1*CRSW(PreferNonGoals,...)
        }

    @property
    def conditions(self):
        return [
            ("heur1", "slots", ["2", "3", "4"]),
            ("heur2", "slots", ["3", "4"]),
            ("heur3", "slots", ["4"]),
        ]
