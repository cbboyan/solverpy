#!/usr/bin/env python3

import os
import shutil
import logging
from enigmatic import lgbtune

from .builder import Builder, NAME
from ..benchmark.path import sids, bids

logger = logging.getLogger(__name__)

class LgbTune(Builder):
   
   def __init__(self, trains, devels=None):
      Builder.__init__(self, trains["dataname"])
      if devels is None:
         devels = trains
      self._trains = trains
      self._devels = devels

   def path(self, modelfile="model.lgb"):
      if modelfile:
         return os.path.join(super().path(), modelfile)
      else:
         return super().path()

   def build(self):
      logger.info(f"Building model: {self._dataname}")
      logger.info(self._trains["trains"].trainid())
  
      f_train = self._trains["trains"].trainid()
      f_test = self._devels["trains"].trainid()
      
      logger.info(f"Tunning learning params: train={f_train} test={f_test}")
      ret = lgbtune.train(
         f_train=f_train,
         f_test=f_test,
         d_tmp=self.path("opt"),
         phases="l:b:m:r",
         timeout=None,
         iters=5,
         min_leaves=2,
         max_leaves=16,
         #init_params=dict(num_round=1000),
      )

      f_best = ret[2]
      f_model = self.path()
      shutil.copyfile(f_best, f_model)
      #self._models = [f_model]
      self._strats = self.applies(self._trains["refs"], self._dataname)

   def apply(self, sid, model):
      tpl = self.template(sid)
      sidml = f"{tpl}@model={model}"
      return [sidml]

   def template(self, sid):
      sidml = f"{sid}-ml"
      if os.path.exists(sids.path(sidml)):
         return sidml
      dbpath = bids.dbpath(NAME)
      mod = f"{dbpath}/@@@model:default@@@/model.lgb"
      strat = sids.load(sid).rstrip()
      strat = self.mlstrat(strat, mod)
      sids.save(sidml, strat)
      return sidml

   def mlstrat(self, strat, model):
      adds = "\n".join([
        f"--ml-engine",
        f"--ml-model={model}"
      ])
      return f"{strat}\n{adds}"

