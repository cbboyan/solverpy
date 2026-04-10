import pytest
from grackle.trainer.bitwuzla.default import BitwuzlaDomain


@pytest.fixture
def domain():
   return BitwuzlaDomain()


# ---------------------------------------------------------------------------
# params
# ---------------------------------------------------------------------------

def test_params_is_dict(domain):
   assert isinstance(domain.params, dict)

def test_params_count(domain):
   assert len(domain.params) == 42

def test_params_bv_solver_values(domain):
   assert "bitblast" in domain.params["bv_solver"]

def test_params_bool_param(domain):
   assert domain.params["abstraction"] == ["true", "false"]

def test_params_no_comments(domain):
   assert all(not k.startswith("#") for k in domain.params)


# ---------------------------------------------------------------------------
# defaults
# ---------------------------------------------------------------------------

def test_defaults_bv_solver(domain):
   assert domain.defaults["bv_solver"] == "bitblast"

def test_defaults_sat_solver(domain):
   assert domain.defaults["sat_solver"] == "cadical"

def test_defaults_covers_all_params(domain):
   for key in domain.params:
      assert key in domain.defaults, f"{key} missing from defaults"


# ---------------------------------------------------------------------------
# conditions
# ---------------------------------------------------------------------------

def test_conditions_count(domain):
   assert len(domain.conditions) == 26

def test_conditions_abstraction_bv_size(domain):
   assert ("abstraction_bv_size", "abstraction", ["true"]) in domain.conditions

def test_conditions_pp_normalize_share_aware(domain):
   assert ("pp_normalize_share_aware", "pp_normalize", ["true"]) in domain.conditions

def test_conditions_compatible_with_load_domain(domain):
   conds_dict = {}
   for (slave, master, vals) in domain.conditions:
      if slave not in conds_dict:
         conds_dict[slave] = {}
      conds_dict[slave][master] = vals
   assert "abstraction_bv_size" in conds_dict
   assert "pp_variable_subst_norm_eq" in conds_dict


# ---------------------------------------------------------------------------
# forbiddens
# ---------------------------------------------------------------------------

def test_forbiddens_empty(domain):
   assert len(domain.forbiddens) == 0


# ---------------------------------------------------------------------------
# dump
# ---------------------------------------------------------------------------

def test_dump_returns_string(domain):
   assert isinstance(domain.dump(), str)

def test_dump_contains_param(domain):
   assert "abstraction {true,false} [false]" in domain.dump()

def test_dump_contains_condition(domain):
   assert "abstraction_bv_size | abstraction in {true}" in domain.dump()

def test_dump_sorted(domain):
   out = domain.dump()
   param_lines = [l for l in out.splitlines() if l.strip() and "{" in l and "[" in l]
   names = [l.split()[0] for l in param_lines]
   assert names == sorted(names)
