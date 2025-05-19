from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
   from ..db import DB
   from ...builder.builder import Builder
   from ...solver.timedsolver import TimedSolver
   from ...solver.plugins.plugin import Plugin
   from ...builder.plugins.trains import Trains

class Setup(TypedDict, total=False):
   cores: int
   ref: (bool | int | str)
   bidfile: str
   sidfile: str
   bidlist: list[str]
   sidlist: list[str]
   delfix: (int | str | None)
   ntfy: str
   it: int
   loops: int
   news: list[str]
   refs: list[str]
   options: list[str]
   dataname: str
   static: str
   basedataname: str
   e_training_examples: str

   db: "DB"
   builder: "Builder"
   solver: "TimedSolver"
   trains: "Trains"
   plugins: list["Plugin"]

   # gen_features
   # limit
   # previous_trains
   # sel_features
   # start_dataname


