from typing import TypedDict

Params = dict[str, str]
"""Solver parameter dict: maps parameter names to their string values."""


class RunnerConfig(TypedDict, total=False):
   """Typed configuration dict for grackle runners.

   All keys are optional (`total=False`).  `Runner.__init__` fills in
   `direct` and `cores`; `GrackleRunner.__init__` adds `dir` and `prefix`.
   Concrete runners fill in `timeout` and `penalty` in their `__init__`.
   """

   # --- core (filled by Runner / GrackleRunner __init__) ---
   direct: bool        # pass params directly vs. load conf by name
   cores: int          # parallel evaluation workers
   dir: str            # confs directory
   prefix: str         # conf filename prefix

   # --- solver settings ---
   timeout: int        # solver time limit (seconds)
   penalty: int        # quality penalty for failed runs

   # --- optional / trainer-set ---
   nick: str           # subdirectory for paramils/ramparils working dir
   extra: str          # extra params joined onto every conf (legacy StageRunner)

   # --- solver-specific binaries / static args ---
   cbinary: str        # cvc5 binary path
   cargs: str          # cvc5 static args
   rlimit: int         # cvc5 resource limit

   vbinary: str        # vampire binary path
   vargs: str          # vampire static args

   lbinary: str        # lash binary path
   lstatic: str        # lash static args

   ebinary: str        # eprover binary path
   eargs: str          # eprover static args
