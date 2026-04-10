import json
import os
from os import path

import ramparils

from .trainer import Trainer
from .stage import StageTrainer


class RamparilsTrainer(Trainer):

   def __init__(self, runner, config={}):
      Trainer.__init__(self, runner, config)

   def domains(self, params):
      return self.runner.domain.dump()

   def improve(self, state, conf, insts, params=None):
      direct = params is not None
      cwd = path.join("training", "iter-%03d-%s" % (state.it, conf))
      cwd = path.join(cwd, self.runner.config["nick"]) if "nick" in self.runner.config else cwd
      params = self.runner.recall(conf) if not direct else params
      if not params:
         params = dict(self.runner.domain.defaults)
         (params, _) = self.runner.domain.split(params)

      os.makedirs(cwd, exist_ok=True)
      f_params = path.abspath(path.join(cwd, "params.txt"))
      open(f_params, "w").write(self.domains(params))

      algo = "grackle-ramparils-wrapper.py %s" % repr(json.dumps(self.runner.config))
      cache_db = path.abspath(path.join("training", "ramparils.db"))

      scenario = {
         "algo": algo,
         "paramfile": f_params,
         "instances": insts,
         "cutoff_time": float(state.trainer.runner.config["timeout"]),
         "tuner_timeout": float(self.trainlimit(len(insts))),
         "run_obj": "quality",
      }

      result = ramparils.specialize(
         strategy={k: str(v) for k, v in params.items()},
         scenario=scenario,
         cache_db=cache_db,
         cores=state.cores,
      )

      params = self.runner.clean(result)
      return params if direct else self.runner.name(params)


class RamparilsStageTrainer(StageTrainer):

   def __init__(self, runner, config={}):
      trainer = RamparilsTrainer(runner, config)
      StageTrainer.__init__(self, runner, trainer, config)
