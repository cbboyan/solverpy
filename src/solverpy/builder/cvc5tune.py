#!/usr/bin/env python3

import os
import logging

from .builder import NAME
from .autotuner import AutoTuner
from ..benchmark.path import sids, bids

logger = logging.getLogger(__name__)

class Cvc5Tune(AutoTuner):
   
   def __init__(self, trains, devels=None, tuneargs=None):
      AutoTuner.__init__(self, trains, devels, tuneargs)

   def template(self, sid):
      sidml = f"{sid}-ml"
      if os.path.exists(sids.path(sidml)):
         logger.debug(f"ml strategy {sidml} already exists")
         return sidml
      dbpath = bids.dbpath(NAME)
      mod = f"{dbpath}/@@@model:default@@@/model.lgb"
      strat = sids.load(sid).rstrip()
      strat = self.mlstrat(strat, mod)
      sids.save(sidml, strat)
      logger.debug(f"created parametric ml strategy {sidml} inherited from {sid}:\n{strat}")
      return sidml

   def mlstrat(self, strat, model):
      adds = "\n".join([
        f"--ml-engine",
        f"--ml-model={model}",
        f"--ml-usage=@@@usage:1.0@@@",
        f"--ml-fallback=@@@fallback:0@@@",
        f"--ml-selector=@@@sel:orig@@@",
        f"--ml-selector-value=@@@val:0.5@@@",
      ])
      return f"{strat}\n{adds}"

   def apply(self, sid, model):
      tpl = self.template(sid)
      sidml = f"{tpl}@model={model}"
      logger.debug(f"new strategy: {sidml}")
      return [sidml]

