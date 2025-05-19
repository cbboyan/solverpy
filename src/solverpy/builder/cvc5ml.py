from typing import Any
import os
import logging

from .builder import NAME
from .autotuner import AutoTuner
from ..benchmark.path import sids, bids

logger = logging.getLogger(__name__)


class Cvc5ML(AutoTuner):

   def __init__(
      self,
      trains: dict[str, Any],
      devels: (dict[str, Any] | None) = None,
      tuneargs: (dict[str, Any] | None) = None,
   ):
      AutoTuner.__init__(
         self,
         trains,
         devels,
         tuneargs,
      )

   def template(self, sid : str) -> str:
      "`sid` must be base strategy without parameters"
      if sid.endswith("-ml"):
         logger.debug(f"strategy {sid} already ml-enhanced")
         return sid
      sidml = f"{sid}-ml"
      if os.path.exists(sids.path(sidml)):
         logger.debug(f"ml strategy {sidml} already exists")
         return sidml
      dbpath = bids.dbpath(NAME)
      mod = f"{dbpath}/@@@model:default@@@/model.lgb"
      strat = sids.load(sid).rstrip()
      strat = self.mlstrat(strat, mod)
      sids.save(sidml, strat)
      logger.debug(
         f"created parametric ml strategy {sidml} inherited from {sid}:\n{strat}"
      )
      return sidml

   def mlstrat(self, strat: str, model: str) -> str:
      adds = "\n".join([
         f"--ml-engine",
         f"--ml-model={model}",
         f"--ml-usage=@@@usage:1.0@@@",
         f"--ml-fallback=@@@fallback:0@@@",
         f"--ml-selector=@@@sel:orig@@@",
         f"--ml-selector-value=@@@val:0.5@@@",
      ])
      return f"{strat}\n{adds}"

   def apply(self, sid: str, model: str) -> list[str]:
      (base, args) = sids.split(sid)
      tpl = self.template(base)
      sidml = sids.fmt(tpl, dict(args, model=model))
      logger.debug(f"new strategy: {sidml}")
      return [sidml]
