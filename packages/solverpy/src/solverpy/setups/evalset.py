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
   limit: str
   cores: int
   binary: str
   static: list[str]
   complete: bool
   force: bool
   shuffle: bool
   solvedby: str
   max_proofs: int
   pool_context: str
   plugin: Any  # SvmTrains
   plugins: list["Plugin"]
   solver: "SolverPy"
   dataname: str
   basedataname: str
   previous_trains: str | tuple[str]
   proofs: dict[str, int] | None
   start_dataname: str
