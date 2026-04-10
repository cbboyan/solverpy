from typing import Any, TYPE_CHECKING

from .config import TrainerConfig, Insts

if TYPE_CHECKING:
   from ..runner.runner import GrackleRunner
   from ..runner.config import Params


class Trainer:

   def __init__(self, runner: "GrackleRunner", config: TrainerConfig = TrainerConfig()):
      self.runner = runner
      self.config = TrainerConfig(config)  # type: ignore[misc]
      self.default("instance_budget", None)
      self.default("log", False)

   def improve(self, state: Any, conf: str, insts: Insts) -> "str | Params | None":
      pass

   def default(self, key: str, val: Any) -> None:
      "Set a default value to the configuration."
      if key not in self.config:
         self.config[key] = val  # type: ignore[literal-required]

   def trainlimit(self, n_inst: int) -> int | float:
      assert "timeout" in self.config
      assert "instance_budget" in self.config
      if self.config["instance_budget"]:
         timeout = n_inst * self.config["instance_budget"]  # type: ignore[operator]
         timeout = min(self.config["timeout"], timeout)
      else:
         timeout = self.config["timeout"]
      return timeout
