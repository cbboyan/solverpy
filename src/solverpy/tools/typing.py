from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
   from ..benchmark.db.provider import Provider
   from ..solver.solverpy import SolverPy

#Bid = str
#"""
#Benchmark identifier.
#"""
#
#Sid = str
#"""
#Strategy identifier.
#"""

Status = str
"""
Solver task status.
"""

ProviderMaker = Callable[[str, str, str], "Provider"]

StrMaker = str | Callable[[Any], str]

SolverMaker = Callable[..., "SolverPy"]

LimitBuilder = dict[str, StrMaker]

Result = dict[str, Any]
"""
Generic solver result.
"""

Report = list["str | Report"]

SolverJob = tuple["SolverPy", str, str]
