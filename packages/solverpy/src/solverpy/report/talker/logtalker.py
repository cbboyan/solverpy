"""
# LogTalker — text-only progress reporter

Reports evaluation progress through Python `logging` calls and writes
Legend/Summary/Statuses to the markdown report via
[`summary`][solverpy.benchmark.summary].  Used in headless or non-interactive
contexts where tqdm bars are not appropriate.

Also provides default log-based implementations of tuning event methods
(`trials`, `trying`, `tried`, `trialed`, `building`, `iteration`, `built`,
etc.) so that subclasses only need to override what they want to change.
"""

from typing import Any, Sequence, TYPE_CHECKING
import logging
import time

from ...benchmark.path import bids
from ...benchmark import summary
from ...tools import human, reporter
from ...benchmark.reports import markdown
from .talker import Talker

if TYPE_CHECKING:
   from ...tools.typing import Result, SolverJob
   from ...task.solvertask import SolverTask
   from ...task.task import Task

logger = logging.getLogger(__name__)


def jobname(solver: Any, bid: str, sid: str) -> str:
   return f"{solver}:{sid} @ {bid}"


class LogTalker(Talker):
   """
   Progress reporter that writes to the Python logger and markdown report.

   ```plantuml name="task-logtalker"
   abstract class solverpy.report.talker.talker.Talker
   class solverpy.report.talker.logtalker.LogTalker extends solverpy.report.talker.talker.Talker {
      - _log_progress: bool
      --
      + begin(jobs, refjob, sidnames, **kwargs)
      + end(results, refjob)
      + next(job)
      + launching(tasks)
      + finished(task, result)
      + done()
      + status(new, n)
      + trials(nick, iters, timeout)
      + trying(nick, it, values)
      + tried(stats)
      + trialed(nick)
      + building(f_mod, total)
      + iteration(n, total, loss)
      + built(score)
      + result(val)
      + tuning(t_start)
      + tuned(t_end)
      + info(msg)
      + debug(msg)
   }
   class solverpy.report.talker.solvertalker.SolverTalker extends solverpy.report.talker.logtalker.LogTalker
   ```

   Calls `summary.legend` in `begin` and `summary.summarize` in `end` to
   write structured tables to the `.md` report file.  Periodic progress
   updates are emitted via `logger.info` at exponentially growing intervals
   so long runs stay observable without flooding the log.

   Set ``log_progress=False`` (as `SolverTalker` does) to demote the
   per-job info lines to ``DEBUG`` — the tqdm bars carry that role instead.

   Tuning event methods (`trials`, `building`, etc.) provide log-based
   default implementations.  `TuneTalker` inherits these and overrides the
   ones that should display tqdm bars instead.
   """

   def __init__(self, log_progress: bool = True):
      """
      Args:
          log_progress: if ``True``, emit ``INFO`` log lines for each job
              and periodic progress updates.  Set to ``False`` when a
              visual progress bar (`SolverTalker`) handles that role.
      """
      super().__init__()
      self._log_progress = log_progress
      self._last_time = None
      # Tuning state shared with TuneTalker
      self._tune_iters: str = ""
      self._tune_header: list[str] | None = None
      self._tune_table: list | None = None
      self._tune_it: int = 0
      self._tune_values: str = ""
      self._tune_desc: str = "trial"
      self._result: Any = None
      # Builder iteration timing
      self._builder_start: float = 0.0
      self._builder_last: float = 0.0
      self._builder_wait: float = 5.0

   def begin(
      self,
      jobs: list["SolverJob"],
      *,
      refjob: "SolverJob | None" = None,
      sidnames: bool = True,
      report: bool = True,
      **kwargs,
   ) -> None:
      """Set up counters, build nick map, write Legend to report, log job count."""
      del kwargs
      self._total_count = sum(len(bids.problems(bid)) for (_, bid, _) in jobs)
      self._total_jobs = len(jobs)
      self._nick_dw = len(str(self._total_jobs))
      self._job_index = 0
      (self._total_nicks_full, self._total_desc) = summary.legend(jobs, refjob, sidnames=sidnames, report=report)
      self._total_nicks = {k[1:3]:v for (k,v) in self._total_nicks_full.items()}
      self._total_errors = 0

      logger.info(f"Evaluating {len(jobs)} jobs with {self._total_count} tasks.")

   def end(
      self,
      results: dict["SolverJob", "Result"],
      refjob: "SolverJob | None" = None,
      report: bool = True,
   ) -> None:
      """Write Summary/Statuses to report, log error count and completion."""
      super().end(results, refjob=refjob)
      if self._total_errors:
         logger.error(
            f"There were errors: {self._total_errors} tasks failed to evaluate."
         )
      if report:
         summary.summarize(results, self._total_nicks_full, refjob)
      logger.info("Evaluation done.")

   def next(self, job: "SolverJob") -> None:
      """Reset per-job counters and log the start of the next job."""
      jname = jobname(*job)
      self._solved = self._unsolved = self._errors = 0
      self._job_index += 1
      nick = self._total_nicks[job[1:3]]
      dw = self._nick_dw
      self._job_desc = f"[{self._job_index:>{dw}}/{self._total_jobs}] {nick}"
      if self._log_progress:
         logger.info(f"Evaluating {jname}")
      logger.debug(f"evaluating {self._job_desc}: {jname}")
      super().next(job)

   def launching(self, tasks: Sequence["Task"]) -> None:
      """Record start time and inject log queue into tasks."""
      self._last_time = time.perf_counter()
      self._start_time = time.perf_counter()
      self._wait_time = 1.0
      self._wait_total = 1
      super().launching(tasks)

   def finished(
      self,
      task: "SolverTask",
      result: "Result",
   ) -> None:
      """Update solved/unsolved/error counters based on the task result."""
      super().finished(task, result)
      self.status(task.status(result))

   def done(self) -> None:
      """Log solved/unsolved/error summary for the completed job."""
      bar = f"+{self._solved} -{self._unsolved} !{self._errors}"
      if self._log_progress:
         logger.info(f"Evaluation done: {bar}")
      else:
         logger.debug(f"evaluation done: {bar}")

   def status(self, new: bool | None, n: int = 1) -> None:
      """
      Update counters and emit periodic progress log lines.

      Args:
          new: ``True`` = solved, ``False`` = unsolved, ``None`` = error.
          n: number of tasks to count (default 1).
      """
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

   # --- Tuning event defaults (log-based) ---

   def trials(self, nick: str, iters: int, timeout: int) -> None:
      """Start a tuning phase: write heading to report and reset trial table."""
      del timeout
      report = markdown.newline() + markdown.heading(f"Tuning `{nick}`", level=3)
      reporter.add(report)
      logger.info(f"Running tuning phase: {nick}")
      self._tune_iters = f"/{iters}" if iters else ""
      self._tune_header = ["it", nick, "score", "test.acc", "train.acc", "time"]
      self._tune_table = []

   def trying(self, nick: str, it: int, values: list) -> None:
      """Record the current trial description; log if ``_log_progress``."""
      del nick
      self._tune_it = it + 1
      vals = ", ".join("%.4f" % v if type(v) is float else str(v) for v in values)
      self._tune_desc = f"[{it+1}{self._tune_iters}] {vals:8s}"
      self._tune_values = vals
      if self._log_progress:
         logger.info(f"Trying {self._tune_desc}")

   def tried(self, stats: dict[str, Any]) -> None:
      """Append the completed trial's stats to the phase table."""
      assert self._tune_table is not None
      self._tune_table.append((
         self._tune_it,
         self._tune_values,
         f"{stats['score']:.4f}",
         human.humanacc(stats["valid_acc"]),
         human.humanacc(stats["train_acc"]),
         human.humantime(stats["duration"]),
      ))

   def trialed(self, nick: str) -> None:
      """Write the completed phase's trial table to the report."""
      del nick
      assert self._tune_table and self._tune_header
      lines = []
      lines.extend(markdown.newline())
      lines.extend(markdown.heading("Trials", level=4))
      lines.extend(markdown.table(
         self._tune_header,
         self._tune_table,
         key=lambda x: float(x[2]),
      ))
      lines.append("")
      reporter.add(lines)
      logger.info(
         f"Tuning phase '{self._tune_header[1]}' done: {len(self._tune_table)} trials."
      )

   def building(self, f_mod: str, total: int) -> None:
      """Log the start of a model build."""
      del total
      self._builder_start = time.perf_counter()
      self._builder_last = time.perf_counter()
      self._builder_wait = 5.0
      logger.debug(f"building model: {f_mod}")
      if self._log_progress:
         logger.info(f"Building model: {f_mod}")

   def iteration(self, n: int, total: int, loss: list[float]) -> None:
      """Emit periodic progress log lines during model training."""
      if n > 3 and (n % 10 != 0):
         return
      elapsed = time.perf_counter() - self._builder_last
      if n > 3 and elapsed < self._builder_wait:
         return
      logme = logger.info if self._log_progress else logger.debug
      msg = "/".join(f"{x:.4f}" for x in loss)
      runtime = time.perf_counter() - self._builder_start
      logme(f"   loss @ {runtime:0.3f}s\t{n:02d}/{total}\t{msg}")
      self._builder_last = time.perf_counter()

   def built(self, score: float) -> None:
      """Log completion of model training."""
      logger.debug(f"model built: score={score:.4f}")

   def result(self, val: Any) -> None:
      """Store the tuning result."""
      self._result = val

   def tuning(self, t_start: float, total: int = 0) -> None:
      del t_start, total

   def tuned(self, t_end: float) -> None:
      del t_end

   def info(self, msg: str) -> None:
      logger.info(msg)

   def debug(self, msg: str) -> None:
      del msg
