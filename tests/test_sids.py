import pytest

from solverpy.benchmark.path.sids import (
   split,
   unspace,
   defaults,
   instatiate,
   fmt,
   name,
)


# --- split ---

def test_split_plain():
   assert split("mysid") == ("mysid", {})


def test_split_single_arg():
   assert split("mysid@x=1") == ("mysid", {"x": "1"})


def test_split_multiple_args():
   sid, args = split("mysid@x=1:y=2")
   assert sid == "mysid"
   assert args == {"x": "1", "y": "2"}


def test_split_whitespace_stripped():
   _, args = split("sid@x = 1")
   assert args == {"x": "1"}


# --- unspace ---

def test_unspace_collapses_spaces():
   assert unspace("--opt1  --opt2   --opt3") == "--opt1 --opt2 --opt3"


def test_unspace_strips_leading_trailing():
   assert unspace("  --opt  ") == "--opt"


def test_unspace_single():
   assert unspace("--opt") == "--opt"


# --- defaults ---

def test_defaults_single():
   assert defaults("@@@ n : 0 @@@") == {"n": "0"}


def test_defaults_multiple():
   strategy = "@@@ a : 1 @@@ and @@@ b : hello @@@"
   assert defaults(strategy) == {"a": "1", "b": "hello"}


def test_defaults_empty():
   assert defaults("--no-params") == {}


# --- instatiate ---

def test_instatiate_replaces():
   result = instatiate("--x=@@@ n : 0 @@@", {"n": "5"})
   assert result == "--x=5"


def test_instatiate_uses_default_when_not_overridden():
   result = instatiate("--x=@@@ n : 42 @@@", {})
   assert result == "--x=42"


def test_instatiate_multiple():
   result = instatiate("@@@ a : 1 @@@ @@@ b : 2 @@@", {"a": "10"})
   assert result == "10 2"


# --- fmt ---

def test_fmt_single():
   assert fmt("sid", {"x": "1"}) == "sid@x=1"


def test_fmt_sorted():
   result = fmt("sid", {"b": "2", "a": "1"})
   assert result == "sid@a=1:b=2"


def test_fmt_empty_args():
   assert fmt("sid", {}) == "sid@"


# --- name ---

def test_name_replaces_slash():
   assert name("a/b/c") == "a--b--c"


def test_name_no_slash():
   assert name("plain") == "plain"
