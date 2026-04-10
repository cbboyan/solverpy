import pytest
from grackle.trainer.eprover.heuristic import HEURISTIC_CEFS, N_CEFS, HeuristicDomain
from grackle.trainer.eprover.ordering import OrderingDomain
from grackle.trainer.eprover.core import CoreDomain
from grackle.trainer.eprover.sine import SineDomain
from grackle.trainer.eprover.default import DefaultDomain


# ── HEURISTIC_CEFS list ───────────────────────────────────────────────────────

def test_heuristic_cefs_count():
    assert N_CEFS == 20
    assert len(HEURISTIC_CEFS) == 20

def test_heuristic_cefs_are_pairs():
    for freq, cef in HEURISTIC_CEFS:
        assert isinstance(freq, int)
        assert freq >= 1
        assert isinstance(cef, str)
        assert "(" in cef and ")" in cef

def test_heuristic_cefs_no_duplicates():
    cefs = [cef for _, cef in HEURISTIC_CEFS]
    assert len(cefs) == len(set(cefs))


# ── HeuristicDomain ────────────────────────────────────────────────────

class TestHeuristicDomain:
    def setup_method(self):
        self.d = HeuristicDomain()

    def test_params_keys(self):
        keys = set(self.d.params)
        assert keys == {"slots", "heur0", "heur1", "heur2", "heur3"}

    def test_slots_values(self):
        assert self.d.params["slots"] == ["1", "2", "3", "4"]

    def test_heur_values_are_indices(self):
        expected = [str(i) for i in range(N_CEFS)]
        for k in ("heur0", "heur1", "heur2", "heur3"):
            assert self.d.params[k] == expected

    def test_defaults(self):
        d = self.d.defaults
        assert d["slots"] == "4"
        assert d["heur0"] == "0"
        assert d["heur1"] == "1"
        assert d["heur2"] == "2"
        assert d["heur3"] == "3"

    def test_conditions_count(self):
        assert len(self.d.conditions) == 3

    def test_conditions_values(self):
        conds = {slave: (master, vals) for slave, master, vals in self.d.conditions}
        assert conds["heur1"] == ("slots", ["2", "3", "4"])
        assert conds["heur2"] == ("slots", ["3", "4"])
        assert conds["heur3"] == ("slots", ["4"])

    def test_no_forbiddens(self):
        assert self.d.forbiddens == []

    def test_dump_contains_slots(self):
        out = self.d.dump()
        assert "slots" in out

    def test_dump_contains_conditions(self):
        out = self.d.dump()
        assert "heur1 | slots in" in out
        assert "heur3 | slots in" in out


# ── OrderingDomain ─────────────────────────────────────────────────────

class TestOrderingDomain:
    def setup_method(self):
        self.d = OrderingDomain()

    def test_params_keys(self):
        assert set(self.d.params) == {"tord", "tord_prec", "tord_weight", "tord_const", "ho_order_kind"}

    def test_tord_values(self):
        assert set(self.d.params["tord"]) == {"LPO4", "KBO6"}

    def test_ho_order_kind_values(self):
        assert set(self.d.params["ho_order_kind"]) == {"lfho", "lambda"}

    def test_defaults(self):
        d = self.d.defaults
        assert d["tord"] == "KBO6"
        assert d["tord_prec"] == "invfreq"
        assert d["tord_weight"] == "precrank10"
        assert d["tord_const"] == "1"
        assert d["ho_order_kind"] == "lfho"

    def test_conditions_kbo_only(self):
        conds = {slave: (master, vals) for slave, master, vals in self.d.conditions}
        assert conds["tord_weight"] == ("tord", ["KBO6"])
        assert conds["tord_const"] == ("tord", ["KBO6"])

    def test_dump_contains_conditions(self):
        out = self.d.dump()
        assert "tord_weight | tord in" in out
        assert "tord_const | tord in" in out


# ── CoreDomain ─────────────────────────────────────────────────────────

class TestCoreDomain:
    def setup_method(self):
        self.d = CoreDomain()

    def test_has_sel(self):
        assert "sel" in self.d.params
        assert "SelectMaxLComplexAvoidAppVar" in self.d.params["sel"]
        assert "PSelectComplexExceptUniqMaxHorn" in self.d.params["sel"]

    def test_has_ho_extension_params(self):
        p = self.d.params
        assert "neg_ext" in p and set(p["neg_ext"]) == {"off", "all"}
        assert "pos_ext" in p and set(p["pos_ext"]) == {"off", "all"}
        assert "ext_sup_max_depth" in p
        assert "lift_lambdas" in p
        assert "local_rw" in p
        assert "fool_unroll" in p
        assert "inverse_recognition" in p
        assert "replace_inj_defs" in p

    def test_has_ho_preprocessing_params(self):
        p = self.d.params
        assert "strong_rw_inst" in p
        assert "no_eq_unfolding" in p
        assert "sos_input_types" in p

    def test_has_satcheck(self):
        p = self.d.params
        assert "satcheck" in p
        assert set(p["satcheck"]) == {"none", "ConjMinMinFreq"}

    def test_has_inference_params(self):
        p = self.d.params
        for key in ("simparamod", "der", "forwardcntxtsr", "fwdemod",
                    "condense", "presat", "splaggr", "srd", "splcl", "defcnf"):
            assert key in p

    def test_defaults_match_nb7(self):
        d = self.d.defaults
        assert d["sel"] == "SelectMaxLComplexAvoidAppVar"
        assert d["simparamod"] == "normal"
        assert d["der"] == "stragg"
        assert d["presat"] == "1"
        assert d["condense"] == "1"
        assert d["neg_ext"] == "all"
        assert d["pos_ext"] == "all"
        assert d["ext_sup_max_depth"] == "0"
        assert d["lift_lambdas"] == "false"
        assert d["local_rw"] == "true"
        assert d["fool_unroll"] == "false"
        assert d["satcheck"] == "ConjMinMinFreq"
        assert d["no_eq_unfolding"] == "1"
        assert d["strong_rw_inst"] == "1"

    def test_no_conditions(self):
        assert self.d.conditions == []

    def test_no_forbiddens(self):
        assert self.d.forbiddens == []

    def test_dump(self):
        out = self.d.dump()
        assert "sel " in out
        assert "neg_ext " in out
        assert "satcheck " in out


# ── SineDomain ─────────────────────────────────────────────────────────

class TestSineDomain:
    def setup_method(self):
        self.d = SineDomain()

    def test_params_keys(self):
        assert set(self.d.params) == {"sine", "sineG", "sineh", "sinegf",
                                       "sineD", "sineR", "sineL", "sineF"}

    def test_sine_binary(self):
        assert self.d.params["sine"] == ["0", "1"]

    def test_defaults(self):
        d = self.d.defaults
        assert d["sine"] == "1"
        assert d["sineG"] == "CountFormulas"
        assert d["sinegf"] == "1.2"

    def test_conditions_all_depend_on_sine(self):
        conds = {slave: (master, vals) for slave, master, vals in self.d.conditions}
        for key in ("sineG", "sineh", "sinegf", "sineD", "sineR", "sineL", "sineF"):
            assert key in conds
            assert conds[key] == ("sine", ["1"])

    def test_dump_contains_conditions(self):
        out = self.d.dump()
        assert "sineG | sine in" in out


# ── DefaultDomain (MultiDomain) ───────────────────────────────────────────────

class TestDefaultDomain:
    def setup_method(self):
        self.d = DefaultDomain()

    def test_has_all_subdomain_params(self):
        params = self.d.params
        # from core
        assert "sel" in params
        assert "neg_ext" in params
        assert "satcheck" in params
        # from ordering
        assert "tord" in params
        assert "ho_order_kind" in params
        # from heuristic
        assert "slots" in params
        assert "heur0" in params

    def test_no_sine_params(self):
        assert "sine" not in self.d.params

    def test_conditions_from_all_subdomains(self):
        cond_slaves = {slave for slave, _, _ in self.d.conditions}
        assert "tord_weight" in cond_slaves   # from ordering
        assert "heur1" in cond_slaves          # from heuristic

    def test_defaults_complete(self):
        d = self.d.defaults
        assert "sel" in d
        assert "tord" in d
        assert "slots" in d

    def test_dump(self):
        out = self.d.dump()
        assert "sel " in out
        assert "tord " in out
        assert "slots " in out
        assert "neg_ext " in out


# ── split() / join() for staged tuning ───────────────────────────────────────

class TestSplitJoin:

    def _full_params(self):
        return dict(DefaultDomain().defaults)

    def test_core_split_keeps_own_params(self):
        d = CoreDomain()
        params = self._full_params()
        mine, other = d.split(params)
        assert set(mine) == set(d.params)
        assert "tord" not in mine       # ordering param
        assert "slots" not in mine      # heuristic param

    def test_ordering_split_keeps_own_params(self):
        d = OrderingDomain()
        params = self._full_params()
        mine, other = d.split(params)
        assert set(mine) == set(d.params)
        assert "sel" not in mine        # core param
        assert "slots" not in mine      # heuristic param

    def test_heuristic_split_keeps_own_params(self):
        d = HeuristicDomain()
        params = self._full_params()
        mine, other = d.split(params)
        assert set(mine) == set(d.params)
        assert "sel" not in mine        # core param
        assert "tord" not in mine       # ordering param

    def test_sine_split_keeps_own_params(self):
        d = SineDomain()
        params = dict(SineDomain().defaults)
        params.update({"sel": "SelectNoLiterals", "tord": "LPO4"})
        mine, other = d.split(params)
        assert set(mine) == set(d.params)
        assert "sel" not in mine
        assert "tord" not in mine

    def test_split_partition_is_complete(self):
        d = CoreDomain()
        params = self._full_params()
        mine, other = d.split(params)
        assert set(mine) | set(other) == set(params)
        assert set(mine) & set(other) == set()

    def test_join_restores_full_params(self):
        d = CoreDomain()
        params = self._full_params()
        mine, other = d.split(params)
        restored = d.join(mine, other)
        assert restored == params

    def test_default_domain_split_chains_subdomains(self):
        # MultiDomain.split() iterates sub-domains; after all stages,
        # everything should be either tunable or fixed.
        d = DefaultDomain()
        params = self._full_params()
        # The MultiDomain chains splits: each sub-domain further reduces params
        # to only its own keys; what's left after chaining is the last domain's keys.
        # More importantly: split then join should round-trip.
        tunable, fixed = d.split(params)
        restored = d.join(tunable, fixed)
        assert set(restored) == set(params)


# ── Runner integration: args() with new domain params ────────────────────────

_RUNNER_CFG = {
    "timeout": "1",
    "domain": "grackle.trainer.eprover.default.DefaultDomain",
}


class TestRunnerArgsNewParams:
    """Smoke-tests for the EproverRunner.args() extensions (no actual E binary needed)."""

    def _make_params(self, **overrides):
        from grackle.trainer.eprover.default import DefaultDomain
        d = DefaultDomain()
        p = dict(d.defaults)
        p.update(overrides)
        return p

    def test_nb7_like_heuristic(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params()
        args = r.args(p)
        # Should contain all 4 nb7 CEFs
        assert "ConjectureRelativeSymbolWeight(PreferGround" in args
        assert "ConjectureRelativeSymbolWeight(ByDerivationDepth" in args
        assert "FIFOWeight(PreferProcessed)" in args
        assert "ConjectureRelativeSymbolWeight(PreferNonGoals" in args

    def test_ho_ext_flags(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params()
        args = r.args(p)
        assert "--neg-ext=all" in args
        assert "--pos-ext=all" in args
        assert "--ext-sup-max-depth=0" in args
        assert "--lift-lambdas=false" in args
        assert "--local-rw=true" in args
        assert "--fool-unroll=false" in args

    def test_satcheck_flag(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params()
        args = r.args(p)
        assert "--satcheck=ConjMinMinFreq" in args
        assert "--satcheck-proc-interval=5000" in args

    def test_no_satcheck_when_none(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params(satcheck="none")
        args = r.args(p)
        assert "--satcheck" not in args

    def test_kbo6_ordering(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params(tord="KBO6", tord_prec="invfreq",
                              tord_weight="precrank10", tord_const="1")
        args = r.args(p)
        assert "-tKBO6" in args
        assert "-Ginvfreq" in args
        assert "-wprecrank10" in args
        assert "-c1" in args

    def test_lpo4_ordering_no_weight(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params(tord="LPO4", tord_prec="arity")
        args = r.args(p)
        assert "-tLPO4" in args
        assert "-Garity" in args
        assert "-w" not in args

    def test_ho_order_kind_lambda(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params(ho_order_kind="lambda")
        args = r.args(p)
        assert "--ho-order-kind=lambda" in args

    def test_strong_rw_inst(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params(strong_rw_inst="1")
        args = r.args(p)
        assert "--strong-rw-inst" in args

    def test_inverse_recognition(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params(inverse_recognition="true")
        args = r.args(p)
        assert "--inverse-recognition" in args

    def test_3_slots(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params(slots="3", heur0="5", heur1="6", heur2="7")
        args = r.args(p)
        # 3 selected CEFs + mandatory completeness CEF
        assert "ConjectureRelativeSymbolWeight(SimulateSOS" in args
        assert "ConjectureRelativeSymbolWeight(ConstPrio" in args
        assert "Refinedweight(SimulateSOS" in args
        assert "FIFOWeight(ConstPrio)" in args

    def test_always_appends_fifo_const_prio(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params(slots="1", heur0="2")  # slot 0 = FIFOWeight(PreferProcessed)
        args = r.args(p)
        # Should have both FIFOWeight variants
        assert "FIFOWeight(PreferProcessed)" in args
        assert "FIFOWeight(ConstPrio)" in args

    def test_clean_removes_unused_heur(self):
        from grackle.runner.eprover import EproverRunner
        r = EproverRunner(_RUNNER_CFG)
        p = self._make_params(slots="2")
        cleaned = r.clean(p)
        assert "heur0" in cleaned
        assert "heur1" in cleaned
        assert "heur2" not in cleaned
        assert "heur3" not in cleaned
