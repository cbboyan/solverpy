from typing import Any, TypeVar, TYPE_CHECKING
import time
import logging

from ...tools import human
from ...task.bar import BuilderBar
from ...benchmark.reports import markdown

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
   T = TypeVar("T")


class Listener:

   def listen(self, message) -> Any:
      #logger.debug(f"listening: {message}")
      try:
         (key, content) = message
      except (TypeError, ValueError):
         logger.exception(f"Incorect message: '{message}'")
         return None
      if not (isinstance(content, tuple) or isinstance(content, list)):
         content = (content, )
      try:
         handler = getattr(self, key)
      except AttributeError:
         logger.warning(
            f"Unknown listener message: {key} (content: {content})")
         return None
      return handler(*content)


class AutotuneListener(Listener):

   def __init__(self, headless: bool = False):
      self._headless = headless
      self.bar = None
      self.desc = "trial"
      self.iters = ""
      self.t_start = 0
      self.t_end = 0
      self.f_mod = None
      self.nick = None
      self.it = None
      self.values = None
      self.table = None
      self.header = None

   def result(self, val: "T") -> "T":
      return val

   def building(self, f_mod: str, total: int) -> None:
      self._last_time = time.perf_counter() 
      self._start_time = time.perf_counter()
      self._wait_time = 5
      logger.debug(f"building model: {f_mod}")
      if self._headless:
         logger.info(f"Building model: {f_mod}")
      else:
         self.bar = BuilderBar(total, self.desc)

   def built(self, score: float) -> None:
      if self.bar:
         self.bar.close()
         self.bar = None
      logger.debug(f"model {self.f_mod} built: score={score:.4f}")

   def status(self, n: int, total: int, loss: list[float]) -> None:
      if self.bar:
         self.bar.status(loss)
      if n > 3 and (n % 10 != 0):
         return
      elapsed = time.perf_counter() - self._last_time
      if n > 3 and elapsed < self._wait_time:
         return
      logme = logger.info if self._headless else logger.debug
      msg = "/".join(f"{x:.4f}" for x in loss)
      runtime = time.perf_counter() - self._start_time
      logme(f"   loss @ {runtime:0.3f}s\t{n:02d}/{total}\t{msg}")
      self._last_time = time.perf_counter()

   def iteration(self, n: int, total: int, loss: list[float]) -> None:
      self.status(n, total, loss)

   def trials(self, nick: str, iters: int, timeout: int) -> None:
      del timeout
      logger.info(
         f"Running tuning phase: {nick}\n> \n> ### Tuning `{nick}` ###\n> ")
      self.iters = f"/{iters}" if iters else ""
      self.header = ["it", nick, "score", "test.acc", "train.acc", "time"]
      self.table = []

   def trying(self, nick: str, it: int, values: list[float]) -> None:
      self.it = it + 1
      self.desc = f"{nick}[{it+1}{self.iters}]"
      self.values = ", ".join("%.4f" % v if type(v) is float else str(v)
                              for v in values)
      self.desc = f"[{it+1}{self.iters}] {self.values:8s}"
      if self._headless:
         logger.info(f"Trying {self.desc}")

   #def tried(self, score, acc, trainacc, duration):
   def tried(self, stats: dict[str, Any]) -> None:
      assert self.table is not None
      self.table.append((
         self.it,
         self.values,
         f"{stats['score']:.4f}",
         human.humanacc(stats["valid_acc"]),
         human.humanacc(stats["train_acc"]),
         human.humantime(stats["duration"]),
      ))

   def trialed(self, nick: str) -> None:
      del nick
      assert self.table and self.header
      lines = []
      lines.append("")
      lines.extend(
         markdown.table(
            self.header,
            self.table,
            key=lambda x: float(x[2]),
         ))
      lines.append("")
      logger.info("\n" + markdown.dump(lines, prefix="> "))

   def tuning(self, t_start: int) -> None:
      self.t_start = t_start

   def tuned(self, t_end: int) -> None:
      self.t_end = t_end

   def info(self, msg: str) -> None:
      logger.info(msg)

   def debug(self, msg: str) -> None:
      #logger.debug(msg)
      pass
