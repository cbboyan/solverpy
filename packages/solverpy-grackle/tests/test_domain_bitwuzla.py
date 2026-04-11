import pytest
from solverpy_grackle.trainer.bitwuzla.default import DefaultDomain
from solverpy_grackle.trainer.bitwuzla.bitwuzla import BitwuzlaDomain


@pytest.fixture
def domain():
   return DefaultDomain()

@pytest.fixture
def bitwuzla():
   return BitwuzlaDomain()


# ---------------------------------------------------------------------------
# DefaultDomain (default — newer API)
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

def test_defaults_bv_solver(domain):
   assert domain.defaults["bv_solver"] == "bitblast"

def test_defaults_sat_solver(domain):
   assert domain.defaults["sat_solver"] == "cadical"

def test_defaults_covers_all_params(domain):
   for key in domain.params:
      assert key in domain.defaults, f"{key} missing from defaults"

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

def test_forbiddens_empty(domain):
   assert len(domain.forbiddens) == 0

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


# ---------------------------------------------------------------------------
# BitwuzlaDomain (bitwuzla — older API)
# ---------------------------------------------------------------------------

def test_bitwuzla_params_count(bitwuzla):
   assert len(bitwuzla.params) == 39

def test_bitwuzla_params_engine_values(bitwuzla):
   assert bitwuzla.params["engine"] == ["aigprop", "fun", "prop", "sls", "quant"]

def test_bitwuzla_params_binary_params(bitwuzla):
   assert bitwuzla.params["normalize"] == ["0", "1"]

def test_bitwuzla_defaults_engine(bitwuzla):
   assert bitwuzla.defaults["engine"] == "fun"

def test_bitwuzla_defaults_sat_engine(bitwuzla):
   assert bitwuzla.defaults["sat_engine"] == "cadical"

def test_bitwuzla_defaults_covers_all_params(bitwuzla):
   for key in bitwuzla.params:
      assert key in bitwuzla.defaults, f"{key} missing from defaults"

def test_bitwuzla_conditions_count(bitwuzla):
   assert len(bitwuzla.conditions) == 2

def test_bitwuzla_conditions_fun_dual_prop_qsort(bitwuzla):
   assert ("fun_dual_prop_qsort", "fun_dual_prop", ["1"]) in bitwuzla.conditions

def test_bitwuzla_conditions_fun_just_heuristic(bitwuzla):
   assert ("fun_just_heuristic", "fun_just", ["1"]) in bitwuzla.conditions

def test_bitwuzla_forbiddens_count(bitwuzla):
   assert len(bitwuzla.forbiddens) == 2

def test_bitwuzla_forbiddens_fun_dual_prop(bitwuzla):
   assert "{fun_dual_prop=1,fun_just=1}" in bitwuzla.forbiddens

def test_bitwuzla_forbiddens_nondestr_subst(bitwuzla):
   assert "{fun_dual_prop=1,nondestr_subst=1}" in bitwuzla.forbiddens

def test_bitwuzla_dump_contains_param(bitwuzla):
   assert "engine {aigprop,fun,prop,sls,quant} [fun]" in bitwuzla.dump()

def test_bitwuzla_dump_contains_condition(bitwuzla):
   assert "fun_dual_prop_qsort | fun_dual_prop in {1}" in bitwuzla.dump()

def test_bitwuzla_dump_contains_forbidden(bitwuzla):
   assert "{fun_dual_prop=1,fun_just=1}" in bitwuzla.dump()
