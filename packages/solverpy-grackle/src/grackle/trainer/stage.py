from .trainer import Trainer
from .domain.multi import MultiDomain
from .. import log

class StageTrainer(Trainer):

   def __init__(self, runner, trainer, config={}):
      assert(isinstance(runner.domain, MultiDomain))
      Trainer.__init__(self, runner, config)
      self._trainer = trainer

   def improve(self, state, conf, insts):
      domain0 = self.runner.domain
      config0 = dict(self.runner.config)
      # TODO: speed up prover launching by removing domain from config
      #       but remove these in ParamilsTrainer.improve
      #       and fix default Runner.clean to ignore keys without defaults
      #self.runner.config = {x:config0[x] for x in config0 if not x.startswith("domain")}
      
      params = self.runner.recall(conf)
      for (i, domain) in enumerate(domain0.domains):
         nick = f"{i+1:02d}-{domain.name}"
         self.runner.domain = domain
         self.runner.config["nick"] = nick
         log.tuner(nick, i+1, len(domain0.domains))
         (params, fixed) = domain.split(params)
         self.runner.config["fixed"] = fixed
         # TODO: adjust timeout (/ n)
         params = self._trainer.improve(state, conf, insts, params=params)
         params = domain.join(params, fixed)
      
      self.runner.domain = domain0
      self.runner.config = config0
      params = self.runner.clean(params)
      return self.runner.name(params)

