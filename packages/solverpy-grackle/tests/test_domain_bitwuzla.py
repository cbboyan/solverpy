import pytest
from grackle.trainer.bitwuzla.domain import BitwuzlaDomain


@pytest.fixture
def domain():
   return BitwuzlaDomain()


# ---------------------------------------------------------------------------
# params
# ---------------------------------------------------------------------------

def test_params_is_dict(domain):
   assert isinstance(domain.params, dict)

def test_params_count(domain):
   assert len(domain.params) == 39

def test_params_engine_values(domain):
   assert domain.params["engine"] == ["aigprop", "fun", "prop", "sls", "quant"]

def test_params_binary_params(domain):
   assert domain.params["normalize"] == ["0", "1"]

def test_params_no_comments(domain):
   assert all(not k.startswith("#") for k in domain.params)


# ---------------------------------------------------------------------------
# defaults
# ---------------------------------------------------------------------------

def test_defaults_engine(domain):
   assert domain.defaults["engine"] == "fun"

def test_defaults_sat_engine(domain):
   assert domain.defaults["sat_engine"] == "cadical"

def test_defaults_covers_all_params(domain):
   for key in domain.params:
      assert key in domain.defaults, f"{key} missing from defaults"


# ---------------------------------------------------------------------------
# conditions
# ---------------------------------------------------------------------------

def test_conditions_count(domain):
   assert len(domain.conditions) == 2

def test_conditions_fun_dual_prop_qsort(domain):
   assert ("fun_dual_prop_qsort", "fun_dual_prop", ["1"]) in domain.conditions

def test_conditions_fun_just_heuristic(domain):
   assert ("fun_just_heuristic", "fun_just", ["1"]) in domain.conditions

def test_conditions_compatible_with_load_domain(domain):
   conds_dict = {}
   for (slave, master, vals) in domain.conditions:
      if slave not in conds_dict:
         conds_dict[slave] = {}
      conds_dict[slave][master] = vals
   assert "fun_dual_prop_qsort" in conds_dict
   assert "fun_just_heuristic" in conds_dict


# ---------------------------------------------------------------------------
# forbiddens
# ---------------------------------------------------------------------------

def test_forbiddens_count(domain):
   assert len(domain.forbiddens) == 2

def test_forbiddens_fun_dual_prop(domain):
   assert "{fun_dual_prop=1,fun_just=1}" in domain.forbiddens

def test_forbiddens_nondestr_subst(domain):
   assert "{fun_dual_prop=1,nondestr_subst=1}" in domain.forbiddens


# ---------------------------------------------------------------------------
# dump
# ---------------------------------------------------------------------------

def test_dump_returns_string(domain):
   assert isinstance(domain.dump(), str)

def test_dump_contains_param(domain):
   assert "engine {aigprop,fun,prop,sls,quant} [fun]" in domain.dump()

def test_dump_contains_condition(domain):
   assert "fun_dual_prop_qsort | fun_dual_prop in {1}" in domain.dump()

def test_dump_contains_forbidden(domain):
   assert "{fun_dual_prop=1,fun_just=1}" in domain.dump()

def test_dump_sorted(domain):
   out = domain.dump()
   param_lines = [l for l in out.splitlines() if l.strip() and "{" in l and "[" in l]
   names = [l.split()[0] for l in param_lines]
   assert names == sorted(names)
