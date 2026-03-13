import pytest

from solverpy.solver.plugins.shell.limits import Limits


def make(limit: str) -> Limits:
   return Limits(limit, {})


# --- parsing ---

def test_timeout_only():
   lim = make("T5")
   assert lim.timeout == 5
   assert lim.memory is None
   assert lim.limit == "T5"


def test_timeout_large():
   lim = make("T300")
   assert lim.timeout == 300


def test_timeout_and_memory():
   lim = make("T10-M512")
   assert lim.timeout == 10
   assert lim.memory == 512.0


def test_str():
   assert str(make("T5")) == "T5"
   assert str(make("T10-M512")) == "T10-M512"


def test_missing_T_raises():
   with pytest.raises((AssertionError, Exception)):
      make("M512")


# --- comparison ---

def test_lt_timeout():
   assert make("T5") < make("T10")
   assert not (make("T10") < make("T5"))


def test_lt_equal():
   assert not (make("T5") < make("T5"))


def test_gt_timeout():
   assert make("T10") > make("T5")


# --- builder ---

def test_builder_string_format():
   lim = Limits("T5", {"T": "--time-limit=%s"})
   assert lim.strategy == "--time-limit=5"


def test_builder_callable():
   lim = Limits("T5", {"T": lambda x: f"--cpu={x}"})
   assert lim.strategy == "--cpu=5"


def test_builder_empty():
   lim = Limits("T5", {})
   assert lim.strategy == ""


# --- strategy property ---

def test_strategy_cmdline():
   lim = Limits("T5", {"T": "--time=%s"}, cmdline=True)
   assert lim.strategy == "--time=5"


def test_strategy_no_cmdline():
   lim = Limits("T5", {"T": "--time=%s"}, cmdline=False)
   assert lim.strategy == "--time=5"
