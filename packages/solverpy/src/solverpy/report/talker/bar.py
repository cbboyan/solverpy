from typing import Any

import datetime
from tqdm import tqdm

BAR_WIDTH = 46
BAR_CHARS = "░▒▓█"

COLOUR_MAP = {
   "green": "\033[32m",
   "blue": "\033[34m",
   "red": "\033[31m",
}
COLOUR_END = "\033[0m"

RED = '\033[91m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
END = '\033[0m'

BAR_DEFAULT = "{desc}: {percentage:6.2f}%|{bar_fixed}| [{elapsed}<{speta}] {n_fmt}/{total_fmt}{postfix}"
BAR_BUILDER = "{desc}: {percentage:6.2f}%|{bar_fixed}| [{elapsed}<{remaining}] {n_fmt}/{total_fmt} {loss}{postfix}"
BAR_RUNNING = "{desc}: {percentage:6.2f}%|{bar_fixed}| [{elapsed}<{speta}] {n_fmt}/{total_fmt} {errors}{pad}{postfix}"
BAR_SOLVING = "{desc}: {percentage:6.2f}%|{bar_fixed}| [{elapsed}<{speta}] {n_fmt}/{total_fmt} {solved}/{unsolved}/{errors}/{solved_eta}{pad}{postfix}"


def _build_bar(n: int, total: int, colour: str = "") -> str:
   frac = min(n / total, 1.0) if total else 0
   filled = frac * BAR_WIDTH
   bar_length = int(filled)
   frac_idx = int((filled - bar_length) * (len(BAR_CHARS) - 1))
   bar = BAR_CHARS[-1] * bar_length
   if bar_length < BAR_WIDTH:
      bar += BAR_CHARS[frac_idx]
      bar += BAR_CHARS[0] * (BAR_WIDTH - bar_length - 1)
   if colour:
      bar = f"{colour}{bar}{COLOUR_END}"
   return bar


class DefaultBar(tqdm):

   def __init__(
      self,
      total: int,
      desc: str,
      ascii: str = "░▒▓█",
      colour: str = "green",
      bar_format: str = BAR_DEFAULT,
      *args: Any,
      **kwargs: Any,
   ):
      self._bar_colour = COLOUR_MAP.get(colour, "")
      tqdm.__init__(
         self,
         total=total,
         desc=desc,
         bar_format=bar_format,
         ascii=ascii,
         colour=colour,
         *args,
         **kwargs,
      )

   @property
   def format_dict(self) -> Any:
      d = super().format_dict
      speta = d["elapsed"] * (d["total"] or 0) / max(d["n"], 1)
      speta -= d["elapsed"]
      speta = str(datetime.timedelta(seconds=int(speta)))
      if speta.startswith("0:"):
         speta = speta[2:]
      d.update(
         speta=speta,
         bar_fixed=_build_bar(d["n"], d["total"] or 0, self._bar_colour),
      )
      return d

   def status(self, status: Any, n: int = 1) -> None:
      del status  # unused argument
      self.update(n)


class BuilderBar(tqdm):

   def __init__(
      self,
      total: int,
      desc: str,
      ascii: str = "░▒▓█",
      colour: str = "green",
      bar_format: str = BAR_BUILDER,
      *args: Any,
      **kwargs: Any,
   ):
      self._loss = []
      self._bar_colour = COLOUR_MAP.get(colour, "")
      tqdm.__init__(
         self,
         total=total,
         desc=desc,
         bar_format=bar_format,
         ascii=ascii,
         colour=colour,
         *args,
         **kwargs,
      )

   @property
   def format_dict(self) -> Any:
      d = super().format_dict
      d.update(
         loss=self._loss,
         bar_fixed=_build_bar(d["n"], d["total"] or 0, self._bar_colour),
      )
      return d

   def status(
      self,
      metrics: dict[str, dict[str, float]],
      n: int = 1,
   ) -> None:
      self._loss = "/".join(f"{value:.4f}" for values in metrics.values()
                            for value in values.values())
      self.update(n)


def _postfix_width(total: int) -> int:
   dw = len(str(total or 0))
   return 6 + 4 * dw  # visible chars of "+s/u/!e/?eta" at max digits


class RunningBar(DefaultBar):

   def __init__(
      self,
      total: int,
      desc: str,
      bar_format: str = BAR_RUNNING,
      postfix_width: int = 0,
      *args: Any,
      **kwargs: Any,
   ):
      self._errors = 0
      self._postfix_width = postfix_width
      DefaultBar.__init__(
         self,
         total,
         desc,
         bar_format=bar_format,
         *args,
         **kwargs,
      )

   @property
   def format_dict(self) -> Any:
      d = super().format_dict
      asc = f"!{self._errors}"
      if self._errors:
         asc = f"{RED}{asc}{END}"
      vis = 1 + len(str(self._errors))  # visible chars of "!N"
      pad = " " * max(0, self._postfix_width - vis)
      d.update(errors=asc, pad=pad)
      return d

   def status(self, status: bool | None, n: int = 1) -> None:
      if status is None:
         self._errors += n
      self.update(n)


class SolvingBar(RunningBar):

   def __init__(
      self,
      total: int,
      desc: str,
      bar_format: str = BAR_SOLVING,
      ascii: str = "░▒▓█",
      colour: str = "blue",
      *args: Any,
      **kwargs: Any,
   ):
      self._solved = 0
      self._unsolved = 0
      RunningBar.__init__(
         self,
         total,
         desc,
         bar_format=bar_format,
         ascii=ascii,
         colour=colour,
         *args,
         **kwargs,
      )

   @property
   def format_dict(self) -> Any:
      d = super().format_dict
      total = d["total"] or 0
      solved_eta = int(self._solved * (total / max(d["n"], 1)))
      pw = _postfix_width(total)
      vis = (1 + len(str(self._solved)) + 1 + len(str(self._unsolved)) + 2 +
             len(str(self._errors)) + 2 + len(str(solved_eta)))
      pad = " " * max(0, pw - vis)
      d.update(
         solved=f"{PURPLE}+{self._solved}{END}",
         unsolved=f"{BLUE}{self._unsolved}{END}",
         solved_eta=f"{PURPLE}?{solved_eta}{END}",
         pad=pad,
      )
      return d

   def status(
      self,
      status: bool | None,
      n: int = 1,
   ) -> None:
      if status is True:
         self._solved += n
      elif status is False:
         self._unsolved += n
      else:  # status is None:
         self._errors += n
      self.update(n)
