from typing import Pattern, Callable, TypeVar
import re


def single(pattern: Pattern, output: str, default: str) -> str:
   mo = re.search(pattern, output)
   return mo.group(1) if mo else default


def keyval(
   pattern: Pattern,
   output: str,
   table: (dict[str, str] | None) = None,
) -> dict[str, str]:
   res = dict(re.findall(pattern, output))
   if table:
      res = {table[x]: res[x] for x in table if x in res}
   return res


def valkey(
   pattern: Pattern,
   output: str,
   table: (dict[str, str] | None) = None,
) -> dict[str, str]:
   res = {k: v for (v, k) in re.findall(pattern, output)}
   if table:
      res = {table[x]: res[x] for x in table if x in res}
   return res


K = TypeVar("K")
U = TypeVar("U")
V = TypeVar("V")

def mapval(
   data: dict[K, U],
   apply: Callable[[U], V],
) -> dict[K, V]:
   return {x: apply(y) for (x, y) in data.items()}
