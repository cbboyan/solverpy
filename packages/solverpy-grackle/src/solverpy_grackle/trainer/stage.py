from typing import Any, TYPE_CHECKING

from .trainer import Trainer
from .config import TrainerConfig, Insts
from .domain.multi import MultiDomain
from .. import log

if TYPE_CHECKING:
   from ..runner.runner import GrackleRunner


class StageTrainer(Trainer):

   def __init__(self, runner: "GrackleRunner", trainer: Trainer, config: TrainerConfig = TrainerConfig()):
      assert isinstance(runner.domain, MultiDomain)
      Trainer.__init__(self, runner, config)
      self._trainer = trainer

   def improve(self, state: Any, conf: str, insts: Insts) -> str:
      assert self.runner.domain
      assert isinstance(self.runner.domain, MultiDomain)
      domain0 = self.runner.domain
      config0 = dict(self.runner.config)

      params = self.runner.recall(conf)
      for (i, domain) in enumerate(domain0.domains):
         nick = f"{i+1:02d}-{domain.name}"
         self.runner.domain = domain
         self.runner.config["nick"] = nick  # type: ignore[typeddict-item]
         log.tuner(nick, i+1, len(domain0.domains))
         (params, fixed) = domain.split(params)
         self.runner.config["fixed"] = fixed  # type: ignore[typeddict-item]
         params = self._trainer.improve(state, conf, insts, params=params)  # type: ignore[call-arg]
         params = domain.join(params, fixed)  # type: ignore[arg-type]

      self.runner.domain = domain0
      self.runner.config = config0  # type: ignore[assignment]
      params = self.runner.clean(params)  # type: ignore[arg-type]
      assert params is not None
      return self.runner.name(params)
