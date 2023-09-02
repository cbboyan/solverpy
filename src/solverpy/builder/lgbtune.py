#!/usr/bin/env python3

import os
import shutil
import logging
from enigmatic import lgbtune

from .builder import Builder, NAME

logger = logging.getLogger(__name__)

TUNEARGS = dict(
   phases="l:b:m:r",
   timeout=None,
   iters=5,
   min_leaves=2,
   max_leaves=16,
   #init_params=dict(num_round=1000),
)

class LgbTune(Builder):
   
   def __init__(self, trains, devels=None, tuneargs=None):
      Builder.__init__(self, trains["dataname"])
      if devels is None:
         devels = trains
      self._trains = trains
      self._devels = devels
      self._tuneargs = dict(TUNEARGS)
      if tuneargs:
         self._tuneargs.update(tuneargs)

   def path(self, modelfile="model.lgb"):
      if modelfile:
         return os.path.join(super().path(), modelfile)
      else:
         return super().path()

   def build(self):
      logger.info(f"Building model: {self._dataname}")
      logger.debug(f'using trains: {self._trains["trains"].path()}')
  
      f_train = self._trains["trains"].path()
      f_test = self._devels["trains"].path()
      
      logger.info(f"Tunning learning params: train={f_train} test={f_test}")
      ret = lgbtune.train(
         f_train=f_train,
         f_test=f_test,
         d_tmp=self.path("opt"),
         **self._tuneargs
      )

      f_best = ret[2]
      f_model = self.path()
      shutil.copyfile(f_best, f_model)
      #self._models = [f_model]
      self._strats = self.applies(self._trains["refs"], self._dataname)

