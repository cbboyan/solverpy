from typing import Any, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
   from ..solver.solverpy import SolverPy
   from ..solver.plugins.plugin import Plugin


class Evalset(TypedDict, total=False):
   """Per-dataset configuration: problems, strategies, and ML training state."""
   label: str
   benchmarks: list[str]
   strategies: list[str]
   bidfile: str
   sidfile: str
   refs: list[str]
   ref: bool | int | str | None
   plugin: Any  # SvmTrains
   plugins: list["Plugin"]
   solver: "SolverPy"
   dataname: str
   basedataname: str
   previous_trains: str | tuple[str]
   proofs: dict[str, int] | None
   start_dataname: str
