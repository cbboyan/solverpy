import pytest
from grackle.trainer.cvc5.domain_base import Cvc5BaseDomain
from grackle.trainer.cvc5.domain import Cvc5Domain


@pytest.fixture
def base():
   return Cvc5BaseDomain()

@pytest.fixture
def domain():
   return Cvc5Domain()


# ---------------------------------------------------------------------------
# Cvc5BaseDomain — params
# ---------------------------------------------------------------------------

def test_base_params_is_dict(base):
   assert isinstance(base.params, dict)

def test_base_params_count(base):
   assert len(base.params) == 43

def test_base_has_full_saturate_quant(base):
   assert base.params["full_saturate_quant"] == ["yes", "no"]

def test_base_has_finite_model_find(base):
   assert "finite_model_find" in base.params

def test_base_no_comments_in_keys(base):
   assert all(not k.startswith("#") for k in base.params)


# ---------------------------------------------------------------------------
# Cvc5BaseDomain — defaults
# ---------------------------------------------------------------------------

def test_base_defaults_full_saturate_quant(base):
   assert base.defaults["full_saturate_quant"] == "no"

def test_base_defaults_e_matching(base):
   assert base.defaults["e_matching"] == "yes"

def test_base_defaults_covers_all_params(base):
   for key in base.params:
      assert key in base.defaults, f"{key} missing from defaults"


# ---------------------------------------------------------------------------
# Cvc5BaseDomain — conditions
# ---------------------------------------------------------------------------

def test_base_conditions_nonempty(base):
   assert len(base.conditions) > 0

def test_base_conditions_are_tuples(base):
   for c in base.conditions:
      assert len(c) == 3

def test_base_conditions_macros_quant_mode(base):
   assert ("macros_quant_mode", "macros_quant", ["yes"]) in base.conditions

def test_base_conditions_uf_ss(base):
   assert ("uf_ss", "finite_model_find", ["yes"]) in base.conditions

def test_base_conditions_compatible_with_load_domain(base):
   # Simulate what load_domain does: iterate as 3-tuples
   conds_dict = {}
   for (slave, master, vals) in base.conditions:
      if slave not in conds_dict:
         conds_dict[slave] = {}
      conds_dict[slave][master] = vals
   assert "macros_quant_mode" in conds_dict


# ---------------------------------------------------------------------------
# Cvc5BaseDomain — dump
# ---------------------------------------------------------------------------

def test_base_dump_contains_param(base):
   assert "full_saturate_quant {yes,no} [no]" in base.dump()

def test_base_dump_contains_condition(base):
   out = base.dump()
   assert "macros_quant_mode | macros_quant in {yes}" in out


# ---------------------------------------------------------------------------
# Cvc5Domain (full) — params
# ---------------------------------------------------------------------------

def test_domain_params_count(domain):
   assert len(domain.params) == 162

def test_domain_has_arith_params(domain):
   assert "arith_brab" in domain.params
   assert "arith_prop" in domain.params

def test_domain_no_comments_in_keys(domain):
   assert all(not k.startswith("#") for k in domain.params)

def test_domain_defaults_covers_all_params(domain):
   for key in domain.params:
      assert key in domain.defaults, f"{key} missing from defaults"


# ---------------------------------------------------------------------------
# Cvc5Domain (full) — conditions
# ---------------------------------------------------------------------------

def test_domain_conditions_nonempty(domain):
   assert len(domain.conditions) > 0

def test_domain_conditions_cbqi_dependencies(domain):
   cond_keys = [c[0] for c in domain.conditions]
   assert "cegqi_all" in cond_keys
   assert "cegqi_bv" in cond_keys

def test_domain_conditions_compatible_with_load_domain(domain):
   conds_dict = {}
   for (slave, master, vals) in domain.conditions:
      if slave not in conds_dict:
         conds_dict[slave] = {}
      conds_dict[slave][master] = vals
   assert len(conds_dict) > 0


# ---------------------------------------------------------------------------
# Cvc5Domain (full) — forbiddens
# ---------------------------------------------------------------------------

def test_domain_forbiddens_empty(domain):
   assert domain.forbiddens == []


# ---------------------------------------------------------------------------
# Cvc5Domain (full) — dump
# ---------------------------------------------------------------------------

def test_domain_dump_contains_param(domain):
   assert "full_saturate_quant {yes,no} [no]" in domain.dump()

def test_domain_dump_sorted(domain):
   out = domain.dump()
   param_lines = [l for l in out.splitlines() if l.strip() and "{" in l and "[" in l]
   names = [l.split()[0] for l in param_lines]
   assert names == sorted(names)
