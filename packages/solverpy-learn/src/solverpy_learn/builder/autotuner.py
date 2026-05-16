from typing import Any, TYPE_CHECKING
import os
import shutil
import logging

from .builder import Builder
from .autotune import autotune
from solverpy.benchmark.reports import progress, markdown
from solverpy.tools import reporter
from solverpy.setups.setup import Setup
from solverpy.task.solvertalker import SolverTalker
from solverpy.task.remotetalker import RemoteTalker
from solverpy.task.logtalker import LogTalker

if TYPE_CHECKING:
   from solverpy.task.talker import Talker

logger = logging.getLogger(__name__)

TUNEARGS = dict(
   phases="l:b:m:r",
   timeout=None,
   iters=8,
   min_leaves=2,
   max_leaves=16,
   #init_params=dict(num_round=1000),
)


class AutoTuner(Builder):

   def __init__(
      self,
      trains: Setup,
      devels: (Setup | None) = None,
      tuneargs: (dict[str, Any] | None) = None,
      templates: (list[str] | None) = None,
      talker: "Talker | None" = None,
   ):
      assert "dataname" in trains
      Builder.__init__(self, trains["dataname"])
      self._trains = trains
      self._devels = devels or trains
      self._tuneargs: dict[str, Any] = TUNEARGS | (tuneargs or {})
      self._templates = templates or []
      self._talker = talker

   def represent(self) -> dict[str, Any]:
      return dict(
         cls=f"{self.__class__.__module__}.{self.__class__.__name__}",
         dataname=self._dataname,
         tuneargs=self._tuneargs,
         templates=self._templates,
      )

   def path(self, modelfile: str = "model.lgb") -> str:
      if modelfile:
         return os.path.join(super().path(), modelfile)
      else:
         return super().path()

   @property
   def talker(self):
      return self._talker

   @talker.setter
   def talker(self, talker):
      self._talker = talker

   def build(self) -> None:
      assert "trains" in self._trains
      assert "trains" in self._devels
      assert "refs" in self._trains
      report = markdown.newline() + markdown.heading(f"Building model `{self._dataname}`", level=2)
      reporter.add(report)
      logger.info(f"Building model: {self._dataname}")
      logger.debug(f'using trains: {self._trains["trains"].path()}')

      f_model = self.path()
      if os.path.exists(f_model):
         logger.info(f"Skipped model building; model {self._dataname} exists.")
         self._strats = self.applies(self._trains["refs"], self._dataname)
         return

      f_train = self._trains["trains"].path()
      f_test = self._devels["trains"].path()

      use_builder = ("atpeval" in self._tuneargs) and self._tuneargs["atpeval"]

      logger.info(f"Tunning learning params: train={f_train} test={f_test}")
      assert "options" in self._trains
      headless = "headless" in self._trains["options"]
      if headless:
         self.talker = LogTalker()
      else:
         self.talker = RemoteTalker(SolverTalker())
      self.talker.listening_start()
      try:
         ret = autotune.prettytuner(
            headless=headless,
            f_train=f_train,
            f_test=f_test,
            d_tmp=self.path("opt"),
            builder=self if use_builder else None,
            **self._tuneargs,
         )
      except KeyboardInterrupt:
         self.talker.terminate()
         raise
      self.talker.listening_stop()

      #f_best = ret[3]
      (score, acc, trainacc, f_best, dur, params, pos, neg) = ret
      (pos, neg) = (int(pos), int(neg))
      shutil.copyfile(f_best, f_model)
      #self._models = [f_model]
      self._strats = self.applies(self._trains["refs"], self._dataname)

      progress.build(self._dataname, *ret)
      logger.info(f"Model {self._dataname} built.")
