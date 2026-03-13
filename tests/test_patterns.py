import re

from solverpy.tools.patterns import single, keyval, valkey, mapval


WORD = re.compile(r"word=(\w+)")
KV = re.compile(r"(\w+)=(\w+)")
VK = re.compile(r"(\w+)=(\w+)")


def test_single_match():
   assert single(WORD, "word=hello", "") == "hello"


def test_single_no_match():
   assert single(WORD, "nothing here", "") == ""
   assert single(WORD, "nothing here", "default") == "default"


def test_single_first_match_only():
   assert single(WORD, "word=first word=second", "") == "first"


def test_keyval_basic():
   result = keyval(KV, "a=1 b=2")
   assert result == {"a": "1", "b": "2"}


def test_keyval_empty():
   assert keyval(KV, "nothing") == {}


def test_keyval_with_table():
   result = keyval(KV, "a=1 b=2 c=3", table={"a": "alpha", "c": "gamma"})
   assert result == {"alpha": "1", "gamma": "3"}
   assert "b" not in result


def test_valkey_basic():
   # valkey swaps value/key: pattern must yield (value, key) pairs
   result = valkey(re.compile(r"(\w+)=(\w+)"), "1=a 2=b")
   assert result == {"a": "1", "b": "2"}


def test_valkey_with_table():
   result = valkey(re.compile(r"(\w+)=(\w+)"), "1=a 2=b", table={"a": "alpha"})
   assert result == {"alpha": "1"}


def test_mapval_basic():
   result = mapval({"a": 1, "b": 2}, lambda x: x * 10)
   assert result == {"a": 10, "b": 20}


def test_mapval_empty():
   assert mapval({}, str) == {}
