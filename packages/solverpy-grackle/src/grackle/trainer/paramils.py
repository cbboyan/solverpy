import json
from typing import Any, TYPE_CHECKING
from os import path

from .trainer import Trainer
from .stage import StageTrainer
from .config import TrainerConfig, Insts
from ..paramils import reparamils

if TYPE_CHECKING:
   from ..runner.runner import GrackleRunner
   from ..runner.config import Params

SCENARIO = """
algo = %s
execdir = .
deterministic = 1
run_obj = runlength
overall_obj = mean
cutoff_time = %s
cutoff_length = max
tunerTimeout = %s
paramfile = params.txt
outdir = paramils-out
instance_file = instances.txt
test_instance_file = empty.tst
"""

class ParamilsTrainer(Trainer):

   def __init__(self, runner: "GrackleRunner", config: TrainerConfig = TrainerConfig()):
      Trainer.__init__(self, runner, config)
      self.default("restarts", False)

   def domains(self, params: "Params") -> str:
      assert self.runner.domain
      return self.runner.domain.dump()

   def improve(self, state: Any, conf: str, insts: Insts, params: "Params | None" = None) -> "str | Params":
      direct = params is not None
      cwd = path.join("training", "iter-%03d-%s" % (state.it, conf))
      cwd = path.join(cwd, self.runner.config["nick"]) if "nick" in self.runner.config else cwd  # type: ignore[typeddict-item]
      params = self.runner.recall(conf) if not direct else params
      if not params:
         assert self.runner.domain
         params = dict(self.runner.domain.defaults)
         (params, _) = self.runner.domain.split(params)
      algo = "grackle-wrapper.py %s" % repr(json.dumps(self.runner.config))
      assert "timeout" in state.trainer.runner.config
      assert "timeout" in state.trainer.config
      scenario = SCENARIO % (algo, state.trainer.runner.config["timeout"], state.trainer.config["timeout"])
      params = reparamils.launch(
         scenario,
         domains=self.domains(params),
         init=params,
         insts=insts,
         cwd=cwd,
         timeout=self.trainlimit(len(insts)),
         restarts=self.config["restarts"],  # type: ignore[typeddict-item]
         cores=state.cores,
         logs=self.config["log"])  # type: ignore[typeddict-item]

      params = self.runner.clean(params)
      return params if direct else self.runner.name(params)  # type: ignore[return-value]


class ParamilsStageTrainer(StageTrainer):

   def __init__(self, runner: "GrackleRunner", config: TrainerConfig = TrainerConfig()):
      trainer = ParamilsTrainer(runner, config)
      StageTrainer.__init__(self, runner, trainer, config)
