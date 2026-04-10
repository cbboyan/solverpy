import pytest
from grackle.trainer.lash.domain import LashDomain, DEFAULTS, PARAMS


@pytest.fixture
def domain():
   return LashDomain()


# ---------------------------------------------------------------------------
# params
# ---------------------------------------------------------------------------

def test_params_is_dict(domain):
   assert isinstance(domain.params, dict)

def test_params_count(domain):
   assert len(domain.params) == 113

def test_params_bool_values(domain):
   assert domain.params["ALL_DEFS_AS_EQNS"] == ["false", "true"]

def test_params_multi_values(domain):
   assert domain.params["AP_WEIGHT"] == ["0", "1", "2", "3", "8", "16", "100", "128"]

def test_params_no_comments(domain):
   assert all(not k.startswith("#") for k in domain.params)


# ---------------------------------------------------------------------------
# defaults
# ---------------------------------------------------------------------------

def test_defaults_is_dict(domain):
   assert isinstance(domain.defaults, dict)

def test_defaults_all_defs_as_eqns(domain):
   assert domain.defaults["ALL_DEFS_AS_EQNS"] == "false"

def test_defaults_choice(domain):
   assert domain.defaults["CHOICE"] == "true"

def test_defaults_covers_all_params(domain):
   for key in domain.params:
      assert key in domain.defaults, f"{key} missing from defaults"


# ---------------------------------------------------------------------------
# conditions / forbiddens
# ---------------------------------------------------------------------------

def test_conditions_empty(domain):
   assert domain.conditions == []

def test_forbiddens_empty(domain):
   assert domain.forbiddens == []


# ---------------------------------------------------------------------------
# dump
# ---------------------------------------------------------------------------

def test_dump_returns_string(domain):
   assert isinstance(domain.dump(), str)

def test_dump_contains_param(domain):
   out = domain.dump()
   assert "AP_WEIGHT {0,1,2,3,8,16,100,128} [1]" in out

def test_dump_contains_all_params(domain):
   out = domain.dump()
   for key in domain.params:
      assert key in out

def test_dump_default_in_brackets(domain):
   out = domain.dump()
   # CHOICE default is "true"
   assert "CHOICE {false,true} [true]" in out

def test_dump_sorted(domain):
   out = domain.dump()
   param_lines = [l for l in out.splitlines() if l.strip() and "{" in l]
   names = [l.split()[0] for l in param_lines]
   assert names == sorted(names)
