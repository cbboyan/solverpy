"""
# Benchmark and strategy paths

Two modules handle path resolution for the two kinds of identifiers used
throughout the benchmark pipeline:

| Module | Identifier | Resolves to |
|---|---|---|
| [`bids`][solverpy.benchmark.path.bids] | benchmark id (`bid`) | directory or file listing problem paths, rooted at `SOLVERPY_BENCHMARKS` |
| [`sids`][solverpy.benchmark.path.sids] | strategy id (`sid`) | strategy definition file in `solverpy_db/strats/`, rooted at `SOLVERPY_DB` |

Both identifiers are plain strings — no slashes in `sid`, forward-slash
path segments in `bid`.  The resolution is always relative to environment
variables so that the same setup dict can be reused across machines.

"""
