from typing import TypedDict

Insts = list[str]
"""List of benchmark instance paths passed to trainer.improve()."""


class TrainerConfig(TypedDict, total=False):
   """Typed configuration dict for grackle trainers.

   All keys are optional (`total=False`).  `Trainer.__init__` fills in
   `instance_budget` and `log`; concrete trainers add `restarts` etc.
   """

   timeout: int          # tuner time limit (seconds)
   instance_budget: int | None  # per-instance time budget (None = use timeout directly)
   restarts: bool        # whether ParamILS should use restarts
   log: bool | str       # log file path or False to disable
