from solverpy.tools.human import (
   humantime,
   humanint,
   humanbytes,
   humanexp,
   numeric,
   indent,
   lindent,
   rindent,
)


def test_humantime_zero():
   assert humantime(0) == "00:00:00.0"


def test_humantime_seconds():
   assert humantime(5.5) == "00:00:05.5"


def test_humantime_minutes():
   assert humantime(90) == "00:01:30.0"


def test_humantime_hours():
   assert humantime(3661) == "01:01:01.0"


def test_humanint_small():
   assert humanint(0) == "0"
   assert humanint(999) == "999"


def test_humanint_thousands():
   assert humanint(1000) == "1,000"
   assert humanint(1000000) == "1,000,000"


def test_humanint_negative():
   assert humanint(-1000) == "-1,000"


def test_humanbytes_bytes():
   assert humanbytes(512) == "512.00 Bytes"


def test_humanbytes_kilobytes():
   assert humanbytes(1024) == "1.00 KB"


def test_humanbytes_megabytes():
   assert humanbytes(1024 * 1024) == "1.00 MB"


def test_humanexp_power_of_two():
   assert humanexp(1) == "2e0"
   assert humanexp(2) == "2e1"
   assert humanexp(1024) == "2e10"


def test_humanexp_non_power():
   assert humanexp(3) == "3"
   assert humanexp(100) == "100"


def test_numeric_int():
   assert numeric("42") == 42
   assert isinstance(numeric("42"), int)


def test_numeric_float():
   assert numeric("3.14") == 3.14
   assert isinstance(numeric("3.14"), float)


def test_numeric_string():
   assert numeric("hello") == "hello"
   assert isinstance(numeric("hello"), str)


def test_indent_left():
   assert lindent("ab", 5) == "   ab"


def test_indent_right():
   assert rindent("ab", 5) == "ab   "


def test_indent_exact_size():
   assert lindent("abc", 3) == "abc"
   assert rindent("abc", 3) == "abc"
