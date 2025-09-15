"""
This module defines a (typed) dictionary [`Setup`][solverpy.setups.Setup] to
store experiment parameters.
"""

from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
   from ..benchmark.db import DB
   from ..builder.builder import Builder
   from ..solver.solverpy import SolverPy
   from ..solver.plugins.plugin import Plugin
   from ..builder.plugins.svm import SvmTrains


class Setup(TypedDict, total=False):
   """
   A (typed) dictionary summarizing the configuration of the experiment.
   An ordinary dictionary can be used in its place but type annotations
   provide additional safety.

   Some parameters should be set by the user, others are automatically
   filled in by functions in the [`setups`][solverpy.setups] module.

   # Evaluation parameters

   The following are the most important parameters to be set by the user for an evaluation run:

   Attributes: 
       limit: Resource limit for solvers.
       cores: Number of CPU cores for parallel evaluation.
       bidlist: List of benchmark ids. 
       sidlist: List of strategy ids.
   
   The following parameters additional parameters for an evaluation run:
   
   Attributes: 
       bidfile: Load benchmark ids from a file.
       sidfile: Load strategy ids from a file.
       ref: Reference strategy id.
       binary: Custom solver binary.  Must be in `PATH`.
       static: Fixed solver options.
       ntfy: Address for user push notifications via [ntfy](https://ntfy.sh).
       options: Experiment boolean options.
           An *option* is identified by its string name, and represents a boolean yes/no value.
           Use `no-`option, like `no-compress`, to set the option to `no`.
           Currently supported options are:
           
           |option|description|default|
           |------|-----------|-------|
           |`outputs`|Keep raw solver output files from all runs.|no|
           |`compress`|Compress output files (outputs, trains, results).|yes|
           |`flatten`|Put all output files in a single directory (replace `/` with `_._`).|yes|
           |`compress-trains`|Compress trains.|yes|
           |`debug-trains`|Dump training data for each file separately.|no|

       plugins: List of additional solver plugins.
       delfix: 
           Prefix to remove from problem names.

           + If the value is of type `str`, then this prefix is removed from the
           beginning of every problem name.
           + If the value is of type `int`, then the problem name is expected to
           be a `/`-separated path, and the first `delfix` components are
           removed.
           + If the value `None`, nothing is removed.

           The typical use is to remove the prefix `problems/` from problem
           names when the problems are stored inside `problems/` subdirectory.
           In that case, set `delfix=1`.

           This applies to DB providers that support `delfix` (e.g.
           [`Solved`][solverpy.benchmark.db.providers.solved] and
           [`Status`][solverpy.benchmark.db.providers.status]).
           The default value is `None`.




  
   # ML parameters

   The following are user options for ML experiments.

   Attributes: 
       loops: Number of iterations of the eval/ML loop.
       refs: Reference strategies.
       force: Recompute everything.
       shuffle: Shuffle problem order.
       dataname: Data id for ML experiments.
       start_dataname: Start the looping with training instead of evaluation.
       max_proofs: Maximum number of proofs per problem for ML experiments.
       e_training_examples: Output format of training samples for `eprover`.
       gen_features: ENIGMA features for generation filtering.
       sel_features: ENIGMA features for clause selection.
       posneg_ratio: Maximum ratio of negative to positive examples.
       templates: Templates for strategy generation.
   
   # Internal parameters

   The following parameters are used internally and should not be set 
   directly by the user.

   Attributes: 
       it: Current iteration number.
       news: New ML strategies.
       basedataname: Original data id.
       db: Database object.
       builder: Builder object.
       solver: Solver object.
       trains: Trains object.
       previous_trains: Training data from the previous iteration.
       proofs: Count of proofs per problem.
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

