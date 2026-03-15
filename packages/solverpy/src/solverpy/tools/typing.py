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

#class SolverJob(tuple):
#    def __new__(cls, solver: "SolverPy", bid: str, sid: str):
#        instance = super().__new__(cls, (solver, bid, sid))
#        return instance
#    
#    @property
#    def solver(self) -> "SolverPy":
#        return self[0]
#    
#    @property
#    def bid(self) -> str:
#        return self[1]
#    
#    @property
#    def sid(self) -> str:
#        return self[2]
#    
#    def __hash__(self):
#        return hash((self.bid, self.sid))
#    
#    def __eq__(self, other):
#        if not isinstance(other, SolverJob):
#            return False
#        return self.bid == other.bid and self.sid == other.sid
    
