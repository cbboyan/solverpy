from solverpy.solver.plugins.status.runhash import RunHash, runhash


def test_runhash_returns_int():
   h = runhash({"a": 1, "b": 2})
   assert isinstance(h, int)
   assert 0 <= h < 2**64


def test_runhash_order_independent():
   assert runhash({"a": 1, "b": 2}) == runhash({"b": 2, "a": 1})


def test_runhash_sensitive_to_values():
   assert runhash({"a": 1}) != runhash({"a": 2})


def test_runhash_empty_is_constant():
   # An empty selection (e.g. a run with none of the wanted keys) always
   # hashes the same fixed value -- not a fingerprint of anything, but a
   # deterministic one two empty runs will agree on.
   assert runhash({}) == runhash({})


def test_runhash_update_sets_int_on_result():
   deco = RunHash(["decisions", "conflicts"])
   result = {"decisions": 3, "conflicts": 1, "runtime": 0.01}
   deco.update(None, None, "", result)

   assert isinstance(result["runhash"], int)
   assert result["runhash"] == runhash({"decisions": 3, "conflicts": 1})


def test_runhash_update_ignores_unselected_keys():
   deco = RunHash(["decisions"])
   a = {"decisions": 3, "runtime": 0.01}
   b = {"decisions": 3, "runtime": 99.0}
   deco.update(None, None, "", a)
   deco.update(None, None, "", b)

   assert a["runhash"] == b["runhash"]


def test_runhash_selected():
   deco = RunHash(["decisions", "conflicts"])
   assert deco.selected("decisions")
   assert not deco.selected("runtime")
