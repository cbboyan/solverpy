"""

# Benchmark identifiers (bid)

Benchmark problem sets are represented by _benchark ids_ (`bid`).  The
_benchmark id_ is a file path relative to the directory in the
`SOLVERPY_BENCHMARKS` environment variable, defaulting to the current working
directory. The file path must point either to a file or to a directory.
If the path leads to a:

* __directory__: then every regular file _directly_ in this directory is considered a benchmark problem.
   Directories and hidden files are ignored and no recursive search is performed.
   This variant is useful when you have a set of problem files, all in one directory.
* __file__: then the file consists of lines containing paths to corresponding problem files.
   The paths are relative to the directory of the `bid` file.  This variant is
   useful when your benchmarks are structured in subdirectories and you don't
   want to merge them into one directory.

Example:
   If  the `bid` is `my/problems/subset1` and this points to a file that
   contains (among others) the line `category1/problem23.smt2` then the
   corresponding problem must be placed in
   `my/problems/category1/problem23.smt2` (because the directory of the `bid`
   file is `my/problems`). 

# Module content

"""

import os

DEFAULT_NAME = "."
DEFAULT_DIR = os.getenv("SOLVERPY_BENCHMARKS", DEFAULT_NAME)

DB_NAME = "solverpy_db"
DB_DIR = os.getenv("SOLVERPY_DB", DB_NAME)


def bidpath(bid: str) -> str:
   """Return the path to the benchmark id file or directory."""
   return os.path.join(DEFAULT_DIR, bid)


def dbpath(subdir: str | None = None) -> str:
   """Return the full path to the database directory."""
   # TODO: move this elsewhere
   return os.path.join(DB_DIR, subdir) if subdir else DB_DIR


def path(
   bid: str,
   problem: str,
   flatten: bool | str = False,
) -> str:
   """
   Return the path to the benchmark problem file.

   Args:
       bid: The benchmark id.
       problem: The problem name.
       flatten: Flatten the problem name so that all problems can be placed in
           the same directory. If `False`, then no flattening is performed. If
           `True`, then `/` is replaced with `_._`. If a string, then `/` is
           replaced with the given string.

   Returns:
       Full path to the problem file.
       
   """
   """Return the path to the problem file."""
   p_bid = bidpath(bid)
   if os.path.isfile(p_bid):
      p_bid = os.path.dirname(p_bid)
   if flatten and problem:
      problem = problem.replace("/", "_._" if flatten is True else flatten)
   return os.path.join(p_bid, problem).rstrip("/")


def name(bid: str, limit: str | None = None) -> str:
   """Translate the benchmark id to a shell-safe name."""
   bid = bid.replace("/", "--")
   if limit:
      bid = f"{bid}--{limit}"
   return bid


def problems(
   bid: str,
   cache: dict[str, list[str]] = {},
) -> list[str]:
   """
   Return the list of all benchmark problems.

   Args:
       bid: The benchmark id.
       cache: The problem cache for every loaded `bid`.  Each `bid` is loaded
           just once.

   Returns:
       The list of all benchmark problems.  The pair (`bid`, `problem`) is
           a unique problem identifier.
   """
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
