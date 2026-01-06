from typing import Any
import os
import shutil
import logging

from .builder import Builder
from .autotune import autotune
from ..benchmark.reports import progress
from ..setups.setup import Setup

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
   ):
      assert "dataname" in trains
      Builder.__init__(self, trains["dataname"])
      self._trains = trains
      self._devels = devels or trains
      self._tuneargs: dict[str, Any] = TUNEARGS | (tuneargs or {})
      self._templates = templates or []

   def path(self, modelfile: str = "model.lgb") -> str:
      if modelfile:
         return os.path.join(super().path(), modelfile)
      else:
         return super().path()

   def build(self) -> None:
      assert "trains" in self._trains
      assert "trains" in self._devels
      assert "refs" in self._trains
      logger.info(
         f"Building model: {self._dataname}\n> \n> ## Building model `{self._dataname}` ##\n> "
      )
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
      ret = autotune.prettytuner(
         f_train=f_train,
         f_test=f_test,
         d_tmp=self.path("opt"),
         builder=self if use_builder else None,
         **self._tuneargs,
      )

      #f_best = ret[3]
      (score, acc, trainacc, f_best, dur, params, pos, neg) = ret
      (pos, neg) = (int(pos), int(neg))
      shutil.copyfile(f_best, f_model)
      #self._models = [f_model]
      self._strats = self.applies(self._trains["refs"], self._dataname)

      report = progress.build(self._dataname, *ret)
      logger.info(f"Model {self._dataname} built.\n{report}")
