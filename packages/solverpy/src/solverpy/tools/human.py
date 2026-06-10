from typing import Any


def indent(string: str, size: int, left: bool = True) -> str:
   if left:
      return (" " * (size - len(string))) + string
   else:
      return string + (" " * (size - len(string)))


def lindent(string: str, size: int) -> str:
   return indent(string, size, left=True)


def rindent(string: str, size: int) -> str:
   return indent(string, size, left=False)


def numeric(strval: str) -> int | float | str:
   if strval.isdigit():
      return int(strval)
   elif strval.replace('.', '', 1).isdigit():
      return float(strval)
   return strval


def format(key: str, val: Any) -> str:
   unit = key[key.rfind(".") + 1:]
   return UNITS[unit](val) if unit in UNITS else str(val)


def humanbytes(
   b: float,
   precision: int = 2,
   separator: str = " ",
   binary_units: bool = False,
) -> str:
   """Format a byte count using powers of 1024.

   Defaults preserve the established display format. Set ``binary_units`` for
   explicit IEC labels such as ``KiB`` and ``MiB``.
   """
   units = (
      ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB")
      if binary_units else
      ("Bytes", "KB", "MB", "GB", "TB", "PB", "EB")
   )
   value = float(b)
   unit = 0
   while abs(value) >= 1024 and unit < len(units) - 1:
      value /= 1024
      unit += 1
   return f"{value:.{precision}f}{separator}{units[unit]}"


def humanint(n: int) -> str:
   s = str(int(abs(n)))
   r = s[-3:]
   s = s[:-3]
   while s:
      r = s[-3:] + "," + r
      s = s[:-3]
   return r if n >= 0 else "-%s" % r


def humantime(s: float) -> str:
   h = s // 3600
   s -= 3600 * h
   m = s // 60
   s -= 60 * m
   return "%02d:%02d:%04.1f" % (h, m, s)


exps_2 = {2**n: n for n in range(256)}


def humanexp(n: int) -> str:
   if n in exps_2:
      return "2e%s" % exps_2[n]
   return str(n)


def humanloss(xy: tuple[float, str]) -> str:
   (x, y) = xy
   return "%.2f [iter %s]" % (x, y)


def humanacc(xyz: Any) -> str:
   if len(xyz) != 3: return str(xyz)
   (acc, pos, neg) = xyz
   return "%.2f%% (%.2f%% / %.2f%%)" % (100 * acc, 100 * pos, 100 * neg)


UNITS = {
   "acc": humanacc,
   "count": humanint,
   "loss": humanloss,
   "time": humantime,
   "seconds": lambda x: "%.2f" % x,
   "size": humanbytes
}
