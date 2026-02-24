from typing import Any, Sequence, TYPE_CHECKING
import logging
import time

from ..benchmark.path import bids
from ..benchmark import summary
from .talker import Talker

if TYPE_CHECKING:
   from ..tools.typing import Result, SolverJob
   from .solvertask import SolverTask
   from .task import Task

logger = logging.getLogger(__name__)


def jobname(solver: Any, bid: str, sid: str) -> str:
   return f"{solver}:{sid} @ {bid}"


class LogTalker(Talker):
   
   def __init__(self, log_progress = True):
      super().__init__()
      self._log_progress = log_progress
      self._last_time = None

   def begin(
      self,
      jobs: list["SolverJob"],
      *,
      refjob: "SolverJob | None" = None,
      sidnames: bool = True,
      **kwargs,
   ):
      del kwargs
      self._total_count = sum(len(bids.problems(bid)) for (_, bid, _) in jobs)
      sum0 = summary.legend(jobs, refjob, sidnames=sidnames)
      (self._total_nicks_full, self._total_desc, self._total_report) = sum0
      self._total_nicks = {k[1:3]:v for (k,v) in self._total_nicks_full.items()}
      self._total_errors = 0

      logger.info(
         f"Evaluating {len(jobs)} jobs with {self._total_count} tasks together:\n{self._total_report}"
      )

   def end(
      self,
      results: dict["SolverJob", "Result"],
      refjob: "SolverJob | None" = None,
   ):
      super().end(results, refjob=refjob)
      if self._total_errors:
         logger.error(
            f"There were errors: {self._total_errors} tasks failed to evaluate."
         )
      report = summary.summarize(results, self._total_nicks_full, refjob)
      logger.info(f"Evaluation done:\n{report}")

   def next(self, job: "SolverJob"):
      jname = jobname(*job)
      self._solved = self._unsolved = self._errors = 0
      self._job_desc = self._total_nicks[job[1:3]] or jname
      if self._log_progress:
         logger.info(f"Evaluating {jname}")
      logger.debug(f"evaluating {self._job_desc}: {jname}")
      super().next(job)
   
   def launching(self, tasks: Sequence["Task"]):
      self._last_time = time.perf_counter()
      self._start_time = time.perf_counter()
      self._wait_time = 1.0
      self._wait_total = 1
      super().launching(tasks)
   
   def finished(
      self,
      task: "SolverTask",
      result: "Result",
   ):
      super().finished(task, result)
      self.status(task.status(result))
   
   def done(self):
      bar = f"+{self._solved} -{self._unsolved} !{self._errors}"
      if self._log_progress:
         logger.info(f"Evaluation done: {bar}")
      else:
         logger.debug(f"evaluation done: {bar}")

   def status(self, new: bool | None, n: int = 1):
      if new is True:
         self._solved += n
      elif new is False:
         self._unsolved += n
      else:  # new is None:
         self._errors += n
      if not self._last_time:
         return
      logme = logger.info if self._log_progress else logger.debug
      elapsed = time.perf_counter() - self._last_time
      after = time.perf_counter() - self._start_time
      bar = f"+{self._solved} -{self._unsolved} !{self._errors}"
      if elapsed > self._wait_time:
         self._last_time = time.perf_counter()
         self._wait_time = self._wait_time * 1.1
         prefix = f"progress @ {after:0.1f}s"
         waiting = f"# waiting {self._wait_time:0.1f}s"
         logme(f"   {prefix}\t{bar}\t{waiting}")
      total = self._solved + self._unsolved + self._errors
      if total >= self._wait_total:
         self._wait_total *= 2
         prefix = f"done {total} @ {after:0.3f}s"
         waiting = f"# waiting {self._wait_total} tasks"
         logme(f"   {prefix}\t{bar}\t{waiting}")


