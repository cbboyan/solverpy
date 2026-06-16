from typing import Any, Callable
import os
import re
import logging

from .builder import Builder, NAME
from .autotuner import AutoTuner
from solverpy.report.talker.talker import Talker
from solverpy.benchmark.path import sids, bids
from .plugins import enigma
from solverpy.setups.setup import Setup
from solverpy.setups.evalset import Evalset

logger = logging.getLogger(__name__)


class EnigmaModel(AutoTuner):

   def __init__(
      self,
      setup: Setup,
      tuneargs: (dict[str, Any] | None),
      variant: str,
      templates: (list[str] | None) = None,
   ):
      AutoTuner.__init__(self, setup, tuneargs, templates)
      self._variant = variant
      assert f"{variant}_features" in setup
      self._features: str = setup[f"{variant}_features"]
      self.reset(self._dataname)

   def featurepath(self) -> str:
      fpath = enigma.featurepath(self._features)
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

   def build(self, talker: Talker = Talker()) -> None:
      super().build(talker)
      self.makemap()

   def makemap(self, mapfile: str | None = None) -> None:
      f_map = mapfile or self.path("enigma.map")
      logger.debug(f"creating enigma map: {f_map}")
      open(f_map, "w").write(f'features("{self._features}").\n')


class EnigmaSel(EnigmaModel):

   def __init__(
      self,
      setup: Setup,
      tuneargs: (dict[str, Any] | None) = None,
      templates: (list[str] | None) = None,
   ):
      EnigmaModel.__init__(
         self,
         setup,
         tuneargs,
         "sel",
         templates,
      )

   def apply(self, sid: str, model: str) -> list[str]:
      (base, args) = sids.split(sid)
      sidsolo = self.template(base, "solo", solo)
      sidsolo = sids.fmt(sidsolo, dict(args, sel=model))
      sidcoop = self.template(base, "coop", coop)
      sidcoop = sids.fmt(sidcoop, dict(args, sel=model))
      news = []
      if "solo" in self._templates:
         news.append(sidsolo)
      if "coop" in self._templates:
         news.append(sidcoop)
      self.makemap(os.path.join(bids.dbpath(NAME), model, "enigma.map"))
      logger.debug(f"new strategies: {news}")
      return news


class EnigmaGen(EnigmaModel):

   def __init__(
      self,
      setup: Setup,
      tuneargs: (dict[str, Any] | None) = None,
      templates: (list[str] | None) = None,
   ):
      EnigmaModel.__init__(
         self,
         setup,
         tuneargs,
         "gen",
         templates,
      )

   def apply(self, sid: str, model: str) -> list[str]:
      if "gen" not in self._templates:
         return []
      (base, args) = sids.split(sid)
      sidgen = self.template(base, "gen", gen)
      sidgen = sids.fmt(sidgen, dict(args, gen=model))
      news = [sidgen]
      self.makemap(os.path.join(bids.dbpath(NAME), model, "enigma.map"))
      logger.debug(f"new strategies: {news}")
      return news


class Enigma(EnigmaModel):

   def __init__(
      self,
      setup: Setup,
      tunesel: (dict[str, Any] | None) = None,
      tunegen: (dict[str, Any] | None) = None,
      templates: (list[str] | None) = None,
   ):
      templates = templates or ["coop", "solo", "gen"]
      AutoTuner.__init__(
         self,
         setup,
         tunesel,
         templates=templates,
      )
      assert "evals" in setup
      trains_evalset = setup["evals"]
      assert "plugin" in trains_evalset
      assert "sel_features" in setup
      assert "gen_features" in setup
      sel = setup["sel_features"]
      gen = setup["gen_features"]
      self._features = sel or gen or ""

      setup_sel = setup
      setup_gen = setup
      if sel and gen:
         # split the multi train data for sel and gen sub-builders
         assert isinstance(trains_evalset["plugin"], enigma.EnigmaMultiTrains)
         plugin = trains_evalset["plugin"]
         setup_sel = Setup(setup)
         setup_sel["evals"] = Evalset(trains_evalset, plugin=plugin._sel)
         setup_gen = Setup(setup)
         setup_gen["evals"] = Evalset(trains_evalset, plugin=plugin._gen)
         if "devels" in setup:
            devels_evalset = setup["devels"]
            assert "plugin" in devels_evalset
            assert isinstance(devels_evalset["plugin"], enigma.EnigmaMultiTrains)
            setup_sel["devels"] = Evalset(devels_evalset, plugin=devels_evalset["plugin"]._sel)
            setup_gen["devels"] = Evalset(devels_evalset, plugin=devels_evalset["plugin"]._gen)

      self._sel = EnigmaSel(setup_sel, tunesel, templates) if sel else None
      self._gen = EnigmaGen(setup_gen, tunegen, templates) if gen else None

   def reset(self, dataname: str) -> None:
      if self._sel:
         self._sel.reset(dataname)
      if self._gen:
         self._gen.reset(dataname)
      Builder.reset(self, dataname)

   def build(self, talker: Talker = Talker()) -> None:
      self._strats = []
      if self._sel:
         self._sel.build(talker)
         self._strats.extend(self._sel.strategies)
      if self._gen:
         self._gen.build(talker)
         self._strats.extend(self._gen.strategies)
      if self._sel and self._gen:
         trains = self._setup["evals"]
         assert "refs" in trains
         refs = trains["refs"]
         self._strats.extend(self.applies(refs, self._dataname))

   def apply(self, sid: str, model: str) -> list[str]:
      assert self._sel and self._gen
      (base, args) = sids.split(sid)
      sidsolo = f"{base}-solo"
      sidcoop = f"{base}-coop"
      sidsologen = self.template(sidsolo, "gen", gen)
      sidcoopgen = self.template(sidcoop, "gen", gen)
      args = dict(args, sel=self._sel._dataname, gen=self._gen._dataname)
      sidsologen = sids.fmt(sidsologen, args)
      sidcoopgen = sids.fmt(sidcoopgen, args)
      news = []
      if "solo" in self._templates:
         news.append(sidsologen)
      if "coop" in self._templates:
         news.append(sidcoopgen)
      logger.debug(f"new strategies: {news}")
      self.makemap(os.path.join(bids.dbpath(NAME), model, "enigma.map"))
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
