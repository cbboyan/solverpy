#!/usr/bin/env python3

import os
import re
import logging

from .builder import Builder, NAME
from .autotuner import AutoTuner
from ..benchmark.path import sids, bids
from .plugins import enigma 

logger = logging.getLogger(__name__)

def cef(freq, model, efun="EnigmaticLgb", prio="ConstPrio", weights=1, threshold=0.5):
   dbpath = bids.dbpath(NAME)
   freq = f"@@@freq:{freq}@@@"
   prio = f"@@@prio:{prio}@@@"
   model = f"{dbpath}/@@@sel:{model}@@@"
   weights = f"@@@weights:{weights}@@@"
   threshold = f"@@@thrsel:{threshold}@@@"
   return f'{freq}*{efun}({prio},"{model}",{weights},{threshold})'

def solo(sid, *, model="default", noinit=False, efun="EnigmaticLgb", prio="ConstPrio", weights=1, threshold=0.5):
   strat = sids.load(sid)
   assert strat.find("-H'") >= 0
   if noinit:
      strat = strat.replace("--prefer-initial-clauses", "")
   base = strat[:strat.index("-H'")]
   eni = cef(1, model, efun, prio, weights, threshold)
   return f"{base}-H'({eni})'"

def coop(sid, *, model="default", noinit=False, efun="EnigmaticLgb", prio="ConstPrio", weights=1, threshold=0.5):
   strat = sids.load(sid)
   assert strat.find("-H'") >= 0
   if noinit:
      strat = strat.replace("--prefer-initial-clauses", "")
   freq = sum(map(int,re.findall(r"(\d*)\*", strat)))
   eni = cef(freq, model, efun, prio, weights, threshold)
   strat = strat.replace("-H'(", f"-H'({eni},")
   return strat

def solo0(sid, **kwargs):
   return solo(sid, **dict(kwargs, noinit=True))

def coop0(sid, **kwargs):
   return coop(sid, **dict(kwargs, noinit=True))

def gen(sid, *, model="default", threshold=0.1):
   strat = sids.load(sid)
   assert strat.count("-H'") == 1
   dbpath = bids.dbpath(NAME)
   model = f"{dbpath}/@@@gen:{model}@@@"
   threshold = f"@@@thrgen:{threshold}@@@"
   args = f'--enigmatic-gen-model="{model}" --enigmatic-gen-threshold={threshold}'
   return strat.replace("-H'", f"{args} -H'")

class EnigmaModel(AutoTuner):
   
   def __init__(self, trains, devels, tuneargs, variant):
      AutoTuner.__init__(self, trains, devels, tuneargs)
      self._variant = variant
      self._fkey = f"{variant}_features"
      self.reset(self._dataname)
   
   def featurepath(self):
      fpath = enigma.featurepath(self._trains[self._fkey])
      return f"{self._variant}_{fpath}"

   def reset(self, dataname):
      dataname = os.path.join(dataname, self.featurepath())
      super().reset(dataname) # does: self._dataname = dataname

   def template(self, sid, name, mk_strat):
      sidml = f"{sid}-{name}"
      if os.path.exists(sids.path(sidml)):
         logger.debug(f"ml strategy {sidml} already exists")
         return sidml
      strat = mk_strat(sid)
      sids.save(sidml, strat)
      logger.debug(f"created parametric ml strategy {sidml} inherited from {sid}:\n{strat}")
      return sidml

   def build(self):
      super().build()
      f_map = self.path("enigma.map")
      features = self._trains[self._fkey]
      open(f_map, "w").write(f'features("{features}").\n')

   
class EnigmaSel(EnigmaModel):

   def __init__(self, trains, devels=None, tuneargs=None):
      EnigmaModel.__init__(self, trains, devels, tuneargs, "sel")

   def apply(self, sid, model):
      (base, args) = sids.split(sid)
      sidsolo = self.template(base, "solo", solo)
      sidsolo = sids.fmt(sidsolo, dict(args, sel=model))
      sidcoop = self.template(base, "coop", coop)
      sidcoop = sids.fmt(sidcoop, dict(args, sel=model))
      news = [ sidsolo, sidcoop ]
      logger.debug(f"new strategies: {news}")
      return news

class EnigmaGen(EnigmaModel):

   def __init__(self, trains, devels=None, tuneargs=None):
      EnigmaModel.__init__(self, trains, devels, tuneargs, "gen")

   def apply(self, sid, model):
      (base, args) = sids.split(sid)
      sidgen = self.template(base, "gen", gen)
      sidgen = sids.fmt(sidgen, dict(args, gen=model))
      news = [ sidgen ]
      logger.debug(f"new strategies: {news}")
      return news

class Enigma(EnigmaModel):
   
   def __init__(self, trains, devels=None, tuneargs=None):
      AutoTuner.__init__(self, trains, devels, tuneargs)
      sel = trains["sel_features"]
      gen = trains["gen_features"]
      trains0 = trains
      if sel and gen:
         # split the multi train data if it is the case
         trains0 = dict(trains, trains=trains["trains"]._sel)
      self._sel = EnigmaSel(trains0, devels, tuneargs) if sel else None
      trains0 = trains
      if sel and gen:
         trains0 = dict(trains, trains=trains["trains"]._gen)
      self._gen = EnigmaGen(trains0, devels, tuneargs) if gen else None
   
   def reset(self, dataname):
      if self._sel:
         self._sel.reset(dataname)
      if self._gen:
         self._gen.reset(dataname)
      Builder.reset(self, dataname)

   def build(self):
      self._strats = []
      if self._sel: 
         self._sel.build()
         self._strats.extend(self._sel.strategies)
      if self._gen:
         self._gen.build()
         self._strats.extend(self._gen.strategies)
      if self._sel and self._gen:
         refs = self._trains["refs"]
         self._strats.extend(self.applies(refs, self._dataname))
         
   def apply(self, sid, model):
      (base, args) = sids.split(sid)
      sidsolo = f"{base}-solo"
      sidcoop = f"{base}-coop"
      sidsologen = self.template(sidsolo, "gen", gen)
      sidcoopgen = self.template(sidcoop, "gen", gen)
      args = dict(args, sel=self._sel._dataname, gen=self._gen.dataname)
      sidsologen = sids.fmt(sidsologen, args)
      sidcoopgen = sids.fmt(sidcoopgen, args)
      news = [ sidsologen, sidcoopgen ]
      logger.debug(f"new strategies: {news}")
      return news

