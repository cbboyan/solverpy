import json
from os import path

from .trainer import Trainer
from .stage import StageTrainer
from ..paramils import reparamils

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
   
   def __init__(self, runner, config={}):
      Trainer.__init__(self, runner, config)
      self.default("restarts", False)

   def domains(self, params):
      return self.runner.domain.dump()
   
   def improve(self, state, conf, insts, params=None):
      direct = params is not None # conf's params are directly provided
      cwd = path.join("training", "iter-%03d-%s"%(state.it, conf))
      cwd = path.join(cwd, self.runner.config["nick"]) if "nick" in self.runner.config else cwd
      params = self.runner.recall(conf) if not direct else params
      if not params: 
         params = dict(self.runner.domain.defaults)
         (params, _) = self.runner.domain.split(params)
      algo = "grackle-wrapper.py %s" % repr(json.dumps(self.runner.config))
      scenario = SCENARIO % (algo, state.trainer.runner.config["timeout"], state.trainer.config["timeout"])
      params = reparamils.launch(
         scenario, 
         domains=self.domains(params), 
         init=params, 
         insts=insts, 
         cwd=cwd, 
         timeout=self.trainlimit(len(insts)), 
         restarts=self.config["restarts"],
         cores=state.cores,
         logs=self.config["log"])

      params = self.runner.clean(params)
      return params if direct else self.runner.name(params) 

   #def recall(self, conf):
   #   return self.runner.recall(conf)

   #def name(self, params):
   #   return self.runner.name(params)

   #def confname(self):
   #   return self._confname 

class ParamilsStageTrainer(StageTrainer):

   def __init__(self, runner, config={}):
      trainer = ParamilsTrainer(runner, config)
      StageTrainer.__init__(self, runner, trainer, config)

