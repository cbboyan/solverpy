from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
   from ..benchmark.db import DB
   from ..builder.builder import Builder
   from ..solver.solverpy import SolverPy
   from ..solver.plugins.plugin import Plugin
   from ..builder.plugins.svm import SvmTrains


class Setup(TypedDict, total=False):
   """
   Experiment setup configuration.

   Attributes: 
       limit: Resource limit for solvers.
              a longer desc?
              Ok what happens if I put here some really long text?
              Ok what happens if I put here some really long text?
              Ok what happens if I put here some really long text?
              Ok what happens if I put here some really long text?
              Ok what happens if I put here some really long text?
              Ok what happens if I put here some really long text?

              With stuff:
              ```python
              code(2+3)
              call(code)
              ```



       cores: Number of cores to be used.
       ref: 
       bidfile: 
       sidfile: 
       bidlist: 
       sidlist: 
       binary: 
       static: 
       ntfy: 
       it: 
       loops: 
       news: 
       refs: 
       options: 
       delfix: 
       force: 
       shuffle: 
       dataname: 
       start_dataname: 
       basedataname: 
       db: 
       builder: 
       solver: 
       trains: 
       previous_trains: 
       plugins: 
       max_proofs: 
       proofs: 
       e_training_examples: 
       gen_features: 
       sel_features: 
       posneg_ratio: 
       templates: 
   """
   limit: str
   cores: int
   ref: (bool | int | str | None)
   bidfile: str
   sidfile: str
   bidlist: list[str]
   sidlist: list[str]
   binary: str
   static: list[str]
   ntfy: str
   it: int
   loops: int
   news: list[str]
   refs: list[str]
   options: list[str]
   delfix: (int | str | None)

   force: bool
   shuffle: bool

   dataname: str
   start_dataname: str
   basedataname: str
   db: "DB"
   builder: "Builder"
   solver: "SolverPy"
   trains: "SvmTrains"
   previous_trains: str | tuple[str]
   plugins: list["Plugin"]
   max_proofs: int
   proofs: (dict[str, int] | None)

   e_training_examples: str
   gen_features: str
   sel_features: str
   posneg_ratio: float
   templates: list[str]

