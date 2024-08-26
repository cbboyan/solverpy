#!/usr/bin/env python3

import os
import shutil
import logging

from .builder import Builder
from .autotune import autotune

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
   
   def __init__(self, trains, devels=None, tuneargs=None):
      Builder.__init__(self, trains["dataname"])
      self._trains = trains
      self._devels = devels or trains
      self._tuneargs = TUNEARGS | (tuneargs or {})

   def path(self, modelfile="model.lgb"):
      if modelfile:
         return os.path.join(super().path(), modelfile)
      else:
         return super().path()

   def build(self):
      logger.info(f"Building model: {self._dataname}")
      logger.debug(f'using trains: {self._trains["trains"].path()}')

      f_model = self.path()
      if os.path.exists(f_model):
         logger.info(f"Skipped model building; model {self._dataname} exists.")
         self._strats = self.applies(self._trains["refs"], self._dataname)
         return
  
      f_train = self._trains["trains"].path()
      f_test = self._devels["trains"].path()
      
      logger.info(f"Tunning learning params: train={f_train} test={f_test}")
      ret = autotune.prettytuner(
         f_train=f_train,
         f_test=f_test,
         d_tmp=self.path("opt"),
         **self._tuneargs
      )

      f_best = ret[2]
      shutil.copyfile(f_best, f_model)
      #self._models = [f_model]
      self._strats = self.applies(self._trains["refs"], self._dataname)

