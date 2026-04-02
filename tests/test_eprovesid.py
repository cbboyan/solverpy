import pytest

from solverpy.solver.plugins.db.eprovesid import EProverSid
from solverpy.benchmark.path import sids


INSTANCE = "dummy-problem.p"

OLD_SID = "eprover-bls0f17"
NEW_SID = "eprover-bls0f17-esid"


@pytest.fixture
def plugin():
   return EProverSid()


# --- old format (CLI options string) ---

def test_old_format_returns_cli_options(plugin):
   _, strategy = plugin.translate(INSTANCE, OLD_SID)
   assert strategy == sids.load(OLD_SID)


def test_old_format_instance_unchanged(plugin):
   instance, _ = plugin.translate(INSTANCE, OLD_SID)
   assert instance == INSTANCE


def test_old_format_not_parse_strategy(plugin):
   _, strategy = plugin.translate(INSTANCE, OLD_SID)
   assert not strategy.startswith("--parse-strategy=")


def test_old_format_starts_with_dash(plugin):
   _, strategy = plugin.translate(INSTANCE, OLD_SID)
   assert strategy.startswith("--")


# --- new format (esid block) ---

def test_new_format_returns_parse_strategy(plugin):
   _, strategy = plugin.translate(INSTANCE, NEW_SID)
   assert strategy.startswith("--parse-strategy=")


def test_new_format_path_points_to_sid_file(plugin):
   _, strategy = plugin.translate(INSTANCE, NEW_SID)
   path = strategy[len("--parse-strategy="):]
   assert path == sids.path(NEW_SID)


def test_new_format_instance_unchanged(plugin):
   instance, _ = plugin.translate(INSTANCE, NEW_SID)
   assert instance == INSTANCE


def test_new_format_no_inline_options(plugin):
   _, strategy = plugin.translate(INSTANCE, NEW_SID)
   # strategy must be exactly --parse-strategy=<path>, nothing else
   assert " " not in strategy
