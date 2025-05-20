from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
   from ..benchmark.db.provider import Provider
   from ..solver.solverpy import SolverPy

ProviderMaker = Callable[[str, str, str], "Provider"]

StrMaker = str | Callable[[Any], str]

SolverMaker = Callable[..., "SolverPy"]

Builder = dict[str, StrMaker]  # TODO: rename to LimitBuilder

Result = dict[str, Any]

Report = list["str | Report"]

SolverTask = tuple["SolverPy", str, str]
