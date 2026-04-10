import pytest
from grackle.trainer.vampire.domain import VampireDomain
from grackle.trainer.vampire.domain_full import VampireFullDomain
from grackle.trainer.vampire.domain_casc import VampireCascDomain


@pytest.fixture
def domain():
   return VampireDomain()

@pytest.fixture
def domain_full():
   return VampireFullDomain()

@pytest.fixture
def domain_casc():
   return VampireCascDomain()


# ---------------------------------------------------------------------------
# VampireDomain — params
# ---------------------------------------------------------------------------

def test_params_is_dict(domain):
   assert isinstance(domain.params, dict)

def test_params_count(domain):
   assert len(domain.params) == 43

def test_params_saturation_algorithm(domain):
   assert domain.params["saturation_algorithm"] == ["discount", "fmb", "inst_gen", "lrs", "otter"]

def test_params_selection_values(domain):
   assert "_1" in domain.params["selection"]
   assert "10" in domain.params["selection"]


# ---------------------------------------------------------------------------
# VampireDomain — defaults
# ---------------------------------------------------------------------------

def test_defaults_is_dict(domain):
   assert isinstance(domain.defaults, dict)

def test_defaults_age_weight_ratio(domain):
   assert domain.defaults["age_weight_ratio"] == "__1_1"

def test_defaults_saturation_algorithm(domain):
   assert domain.defaults["saturation_algorithm"] == "lrs"

def test_defaults_covers_all_params(domain):
   for key in domain.params:
      assert key in domain.defaults, f"{key} missing from defaults"


# ---------------------------------------------------------------------------
# VampireDomain — conditions / forbiddens
# ---------------------------------------------------------------------------

def test_conditions_empty(domain):
   assert domain.conditions == []

def test_forbiddens_nonempty(domain):
   assert len(domain.forbiddens) > 0

def test_forbiddens_are_strings(domain):
   for f in domain.forbiddens:
      assert isinstance(f, str)

def test_forbiddens_start_with_brace(domain):
   for f in domain.forbiddens:
      assert f.startswith("{") and f.endswith("}")

def test_forbiddens_inst_gen(domain):
   assert "{age_weight_ratio=__1_2,saturation_algorithm=inst_gen}" in domain.forbiddens

def test_forbiddens_avatar_off(domain):
   assert "{avatar_add_complementary=none,avatar=off}" in domain.forbiddens


# ---------------------------------------------------------------------------
# VampireDomain — dump
# ---------------------------------------------------------------------------

def test_dump_contains_param(domain):
   assert "saturation_algorithm {discount,fmb,inst_gen,lrs,otter} [lrs]" in domain.dump()

def test_dump_contains_forbidden(domain):
   assert "{age_weight_ratio=__1_2,saturation_algorithm=inst_gen}" in domain.dump()

def test_dump_sorted(domain):
   out = domain.dump()
   param_lines = [l for l in out.splitlines() if l.strip() and "{" in l and "[" in l]
   names = [l.split()[0] for l in param_lines]
   assert names == sorted(names)


# ---------------------------------------------------------------------------
# VampireFullDomain — extra params vs VampireDomain
# ---------------------------------------------------------------------------

def test_full_has_more_params(domain, domain_full):
   assert len(domain_full.params) > len(domain.params)

def test_full_has_more_forbiddens(domain, domain_full):
   assert len(domain_full.forbiddens) > len(domain.forbiddens)

def test_full_has_extra_param(domain_full):
   assert "equality_proxy" in domain_full.params

def test_full_defaults_covers_all_params(domain_full):
   for key in domain_full.params:
      assert key in domain_full.defaults, f"{key} missing from defaults"


# ---------------------------------------------------------------------------
# VampireCascDomain — basic checks
# ---------------------------------------------------------------------------

def test_casc_params_count(domain_casc):
   assert len(domain_casc.params) == 51

def test_casc_has_split_at_activation(domain_casc):
   assert "split_at_activation" in domain_casc.params

def test_casc_forbiddens_nonempty(domain_casc):
   assert len(domain_casc.forbiddens) > 0

def test_casc_defaults_covers_all_params(domain_casc):
   for key in domain_casc.params:
      assert key in domain_casc.defaults, f"{key} missing from defaults"
