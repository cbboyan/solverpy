import os

DEFAULT_NAME = "."
DEFAULT_DIR = os.getenv("SOLVERPY_BENCHMARKS", DEFAULT_NAME)

DB_NAME = "solverpy_db"
DB_DIR = os.getenv("SOLVERPY_DB", DB_NAME)


def bidpath(bid: str) -> str:
   return os.path.join(DEFAULT_DIR, bid)


def dbpath(subdir: str | None = None) -> str:
   # TODO: move this elsewhere
   return os.path.join(DB_DIR, subdir) if subdir else DB_DIR


def path(
   bid: str,
   problem: str,
   flatten: bool | str = False,
) -> str:
   p_bid = bidpath(bid)
   if os.path.isfile(p_bid):
      p_bid = os.path.dirname(p_bid)
   if flatten and problem:
      problem = problem.replace("/", "_._" if flatten is True else flatten)
   return os.path.join(p_bid, problem).rstrip("/")


def name(bid: str, limit: str | None = None) -> str:
   bid = bid.replace("/", "--")
   if limit:
      bid = f"{bid}--{limit}"
   return bid


def problems(
   bid: str,
   cache: dict[str, list[str]] = {},
) -> list[str]:
   if bid in cache:
      return cache[bid]
   p_bid = bidpath(bid)
   if os.path.isfile(p_bid):
      probs = open(p_bid).read().strip().split("\n")
   else:  # now os.path.isdir(p_bid) holds
      probs = [x for x in os.listdir(p_bid) \
         if os.path.isfile(os.path.join(p_bid,x))]
   cache[bid] = probs
   return probs
