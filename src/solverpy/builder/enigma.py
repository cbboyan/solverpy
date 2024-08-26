#!/usr/bin/env python3

import os
import re
import logging

from .builder import NAME
from .autotuner import AutoTuner
from ..benchmark.path import sids, bids
from ..solver.plugins.trains import enigma 

logger = logging.getLogger(__name__)

def cef(freq, model, efun="EnigmaticLgb", prio="ConstPrio", weigths=1, threshold=0.5):
   dbpath = bids.dbpath(NAME)
   freq = f"@@@freq:{freq}@@@"
   prio = f"@@@prio:{prio}@@@"
   model = f"{dbpath}/@@@model:{model}@@@"
   weigths = f"@@@weigths:{weigths}@@@"
   threshold = f"@@@threshold:{threshold}@@@"
   return f'{freq}*{efun}({prio},"{model}",{weigths},{threshold})'

def solo(sid, model="default", noinit=False, efun="EnigmaticLgb", prio="ConstPrio", weigths=1, threshold=0.5):
   strat = sids.load(sid)
   assert strat.find("-H'") >= 0
   if noinit:
      strat = strat.eplace("--prefer-initial-clauses", "")
   base = strat[:strat.index("-H'")]
   eni = cef(1, model, efun, prio, weigths, threshold)
   return f"{base}-H'{eni}'"

def coop(sid, model="default", noinit=False, efun="EnigmaticLgb", prio="ConstPrio", weigths=1, threshold=0.5):
   strat = sids.load(sid)
   assert strat.find("-H'") >= 0
   if noinit:
      strat = strat.eplace("--prefer-initial-clauses", "")
   freq = sum(map(int,re.findall(r"(\d*)\*", strat)))
   eni = cef(freq, model, efun, prio, weigths, threshold)
   strat = strat.replace("-H'(", f"-H'({eni},")
   return strat

class Enigma(AutoTuner):
   
   def __init__(self, trains, devels=None, tuneargs=None):
      AutoTuner.__init__(self, trains, devels, tuneargs)
      self.reset(self._dataname)
   
   def featurepath(self):
      return enigma.featurepath(self._trains["sel_features"])

   def reset(self, dataname):
      dataname = os.path.join(dataname, self.featurepath())
      super().reset(dataname)

   def template(self, sid, name, mk_strat):
      sidml = f"{sid}-{name}"
      if os.path.exists(sids.path(sidml)):
         logger.debug(f"ml strategy {sidml} already exists")
         return sidml
      strat = mk_strat(sid, efun="EnigmaticLgb", prio="ConstPrio")
      sids.save(sidml, strat)
      logger.debug(f"created parametric ml strategy {sidml} inherited from {sid}:\n{strat}")
      return sidml

   def apply(self, sid, model):
      sidsolo = self.template(sid, "solo", solo)
      sidsolo = f"{sidsolo}@model={model}"
      sidcoop = self.template(sid, "coop", coop)
      sidcoop = f"{sidcoop}@model={model}"
      news = [ sidsolo, sidcoop ]
      logger.debug(f"new strategies: {news}")
      return news

   def build(self):
      super().build()
      f_map = self.path("enigma.map")
      features = self._trains["sel_features"]
      open(f_map, "w").write(f'features("{features}").\n')

