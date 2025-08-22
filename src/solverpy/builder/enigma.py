from typing import Any, Callable, TYPE_CHECKING
import os
import re
import logging

from .builder import Builder, NAME
from .autotuner import AutoTuner
from ..benchmark.path import sids, bids
from .plugins import enigma
from ..benchmark.setups.setup import Setup

logger = logging.getLogger(__name__)


class EnigmaModel(AutoTuner):

   def __init__(
         self,
         trains: Setup,
         devels: (Setup | None),
         tuneargs: (dict[str, Any] | None),
         variant: str,
   ):
      AutoTuner.__init__(self, trains, devels, tuneargs)
      self._variant = variant
      self._fkey = f"{variant}_features"
      self.reset(self._dataname)

   def featurepath(self) -> str:
      fpath = enigma.featurepath(self._trains[self._fkey])
      return f"{self._variant}_{fpath}"

   def reset(self, dataname: str) -> None:
      dataname = os.path.join(dataname, self.featurepath())
      super().reset(dataname)  # does: self._dataname = dataname

   def template(
      self,
      sid: str,
      name: str,
      mk_strat: Callable[[str], str],
   ) -> str:
      sidml = f"{sid}-{name}"
      if os.path.exists(sids.path(sidml)):
         logger.debug(f"ml strategy {sidml} already exists")
         return sidml
      strat = mk_strat(sid)
      sids.save(sidml, strat)
      logger.debug(
         f"created parametric ml strategy {sidml} inherited from {sid}:\n{strat}"
      )
      return sidml

   def build(self) -> None:
      super().build()
      f_map = self.path("enigma.map")
      features = self._trains[self._fkey]
      open(f_map, "w").write(f'features("{features}").\n')


class EnigmaSel(EnigmaModel):

   def __init__(
      self,
      trains: Setup,
      devels: (Setup | None) = None,
      tuneargs: (dict[str, Any] | None) = None,
   ):
      EnigmaModel.__init__(
         self,
         trains,
         devels,
         tuneargs,
         "sel",
      )

   def apply(self, sid: str, model: str) -> list[str]:
      (base, args) = sids.split(sid)
      sidsolo = self.template(base, "solo", solo)
      sidsolo = sids.fmt(sidsolo, dict(args, sel=model))
      sidcoop = self.template(base, "coop", coop)
      sidcoop = sids.fmt(sidcoop, dict(args, sel=model))
      news = [sidsolo, sidcoop]
      logger.debug(f"new strategies: {news}")
      return news


class EnigmaGen(EnigmaModel):

   def __init__(
      self,
      trains: Setup,
      devels: (Setup | None) = None,
      tuneargs: (dict[str, Any] | None) = None,
   ):
      EnigmaModel.__init__(
         self,
         trains,
         devels,
         tuneargs,
         "gen",
      )

   def apply(self, sid: str, model: str) -> list[str]:
      (base, args) = sids.split(sid)
      sidgen = self.template(base, "gen", gen)
      sidgen = sids.fmt(sidgen, dict(args, gen=model))
      news = [sidgen]
      logger.debug(f"new strategies: {news}")
      return news


class Enigma(EnigmaModel):

   def __init__(
      self,
      trains: Setup,
      devels: (Setup | None) = None,
      tuneargs: (dict[str, Any] | None) = None,
   ):
      AutoTuner.__init__(
         self,
         trains,
         devels,
         tuneargs,
      )
      assert "trains" in trains
      assert "sel_features" in trains
      assert "gen_features" in trains
      sel = trains["sel_features"]
      gen = trains["gen_features"]
      trains0 = trains
      devels0 = devels
      if sel and gen:
         # split the multi train data if it is the case
         assert isinstance(trains["trains"], enigma.EnigmaMultiTrains)
         trains0 = Setup(trains, trains=trains["trains"]._sel)
         if devels:
            assert "trains" in devels
            assert isinstance(devels["trains"], enigma.EnigmaMultiTrains)
            devels0 = Setup(trains, trains=devels["trains"]._sel)
      self._sel = EnigmaSel(trains0, devels0, tuneargs) if sel else None

      trains0 = trains
      devels0 = devels
      if sel and gen:
         assert isinstance(trains["trains"], enigma.EnigmaMultiTrains)
         trains0 = Setup(trains, trains=trains["trains"]._gen)
         if devels:
            assert "trains" in devels
            assert isinstance(devels["trains"], enigma.EnigmaMultiTrains)
            devels0 = Setup(trains, trains=devels["trains"]._gen)
      self._gen = EnigmaGen(trains0, devels0, tuneargs) if gen else None

   def reset(self, dataname: str) -> None:
      if self._sel:
         self._sel.reset(dataname)
      if self._gen:
         self._gen.reset(dataname)
      Builder.reset(self, dataname)

   def build(self) -> None: 
      self._strats = []
      if self._sel:
         self._sel.build()
         self._strats.extend(self._sel.strategies)
      if self._gen:
         self._gen.build()
         self._strats.extend(self._gen.strategies)
      if self._sel and self._gen:
         assert "refs" in self._trains
         refs = self._trains["refs"]
         self._strats.extend(self.applies(refs, self._dataname))

   def apply(self, sid: str, model: str) -> list[str]:
      del model # unused argument
      assert self._sel and self._gen
      (base, args) = sids.split(sid)
      sidsolo = f"{base}-solo"
      sidcoop = f"{base}-coop"
      sidsologen = self.template(sidsolo, "gen", gen)
      sidcoopgen = self.template(sidcoop, "gen", gen)
      args = dict(args, sel=self._sel._dataname, gen=self._gen._dataname)
      sidsologen = sids.fmt(sidsologen, args)
      sidcoopgen = sids.fmt(sidcoopgen, args)
      news = [sidsologen, sidcoopgen]
      logger.debug(f"new strategies: {news}")
      return news


def cef(
   freq: int,
   model: str,
   efun: str = "EnigmaticLgb",
   prio: str = "ConstPrio",
   weights: int = 1,
   threshold: float = 0.5,
):
   dbpath = bids.dbpath(NAME)
   freq0 = f"@@@freq:{freq}@@@"
   prio0 = f"@@@prio:{prio}@@@"
   model0 = f"{dbpath}/@@@sel:{model}@@@"
   weights0 = str(f"@@@weights:{weights}@@@")
   threshold0 = f"@@@thrsel:{threshold}@@@"
   return f'{freq0}*{efun}({prio0},"{model0}",{weights0},{threshold0})'


def solo(
   sid: str,
   *,
   model: str = "default",
   noinit: bool = False,
   efun: str = "EnigmaticLgb",
   prio: str = "ConstPrio",
   weights: int = 1,
   threshold: float = 0.5,
) -> str:
   strat = sids.load(sid)
   assert strat.find("-H'") >= 0
   if noinit:
      strat = strat.replace("--prefer-initial-clauses", "")
   base = strat[:strat.index("-H'")]
   eni = cef(1, model, efun, prio, weights, threshold)
   return f"{base}-H'({eni})'"


def coop(
   sid : str,
   *,
   model: str = "default",
   noinit: bool = False,
   efun: str = "EnigmaticLgb",
   prio: str = "ConstPrio",
   weights: int = 1,
   threshold: float = 0.5,
) -> str:
   strat = sids.load(sid)
   assert strat.find("-H'") >= 0
   if noinit:
      strat = strat.replace("--prefer-initial-clauses", "")
   freq = sum(map(int, re.findall(r"(\d*)\*", strat)))
   eni = cef(freq, model, efun, prio, weights, threshold)
   strat = strat.replace("-H'(", f"-H'({eni},")
   return strat


def solo0(sid: str, **kwargs: Any) -> str:
   return solo(sid, **dict(kwargs, noinit=True))


def coop0(sid: str, **kwargs: Any) -> str:
   return coop(sid, **dict(kwargs, noinit=True))


def gen(sid: str, *, model: str = "default", threshold: float = 0.1) -> str:
   strat = sids.load(sid)
   assert strat.count("-H'") == 1
   dbpath = bids.dbpath(NAME)
   model0 = f"{dbpath}/@@@gen:{model}@@@"
   threshold0 = f"@@@thrgen:{threshold}@@@"
   args = f'--enigmatic-gen-model="{model0}" --enigmatic-gen-threshold={threshold0}'
   return strat.replace("-H'", f"{args} -H'")

