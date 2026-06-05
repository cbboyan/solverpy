"""
# EvalTalker — interactive progress bar reporter

Extends [`LogTalker`][solverpy.report.talker.logtalker.LogTalker] with tqdm progress
bars: a per-job [`SolvingBar`][solverpy.report.talker.bar.SolvingBar] and a cumulative
[`RunningBar`][solverpy.report.talker.bar.RunningBar] across all jobs.  Used in
interactive (terminal) mode; falls back to `LogTalker` text output in
headless mode.
"""

import logging
from typing import TYPE_CHECKING, Sequence

from .logtalker import LogTalker
from ...benchmark.path import bids as _bids
from .bar import SolvingBar, RunningBar, _postfix_width

if TYPE_CHECKING:
   from ...tools.typing import Result, SolverJob
   from ...task.task import Task

logger = logging.getLogger(__name__)


class EvalTalker(LogTalker):
   """
   Interactive progress reporter with tqdm bars.

   ```plantuml name="task-evaltalker"
   abstract class solverpy.report.talker.talker.Talker
   class solverpy.report.talker.logtalker.LogTalker extends solverpy.report.talker.talker.Talker
   class solverpy.report.talker.evaltalker.EvalTalker extends solverpy.report.talker.logtalker.LogTalker {
      - _job_bar: SolvingBar | None
      - _total_bar: RunningBar | None
      --
      + begin(jobs, refjob, sidnames, **kwargs)
      + end(results, refjob)
      + terminate()
      + next(job)
      + launching(tasks)
      + done()
      + status(new, n)
   }
   ```

   Creates two bars on `begin`: a `RunningBar` spanning the entire evaluation
   and a per-job `SolvingBar` created in `launching`.  Both are closed and
   cleared on `terminate`.
   """

   def __init__(self) -> None:
      super().__init__(headless=False)
      self._job_bar: SolvingBar | None = None
      self._total_bar: RunningBar | None = None

   def eval_begin(
      self,
      jobs: list["SolverJob"],
      *,
      refjob: "SolverJob | None" = None,
      sidnames: bool = True,
      miniters: int = 1,
      **kwargs,
   ) -> None:
      """Create the total ``RunningBar`` spanning all jobs."""
      super().eval_begin(jobs, refjob=refjob, sidnames=sidnames, **kwargs)
      dw = self._nick_dw
      prefix_len = 2 * dw + 3  # "[n/m] " without trailing space
      total_desc = f"{' ' * prefix_len} {self._total_desc}"
      max_job = max(len(_bids.problems(bid)) for (_, bid, _) in jobs)
      self._total_bar = RunningBar(
         total=self._total_count,
         desc=total_desc,
         miniters=miniters,
         postfix_width=_postfix_width(max_job),
      )

   def eval_end(
      self,
      results: dict["SolverJob", "Result"],
      refjob: "SolverJob | None" = None,
      **kwargs,
   ) -> None:
      """Harvest error count from the total bar if present, then delegate to ``LogTalker.eval_end``."""
      if self._total_bar:
         self._total_errors = self._total_bar._errors
      super().eval_end(results, refjob=refjob, **kwargs)

   def terminate(self) -> None:
      """Close and discard both bars, then stop the log queue."""
      super().terminate()
      if self._total_bar:
         self._total_bar.close()
         self._total_bar = None
      if self._job_bar:
         self._job_bar.close()
         self._job_bar = None

   def eval_next(self, job: "SolverJob") -> None:
      super().eval_next(job)

   def eval_launch(self, tasks: Sequence["Task"]) -> None:
      """Create the per-job ``SolvingBar`` and inject the log queue into tasks."""
      super().eval_launch(tasks)
      self._job_bar = SolvingBar(len(tasks), self._job_desc, miniters=1)

   def eval_done(self) -> None:
      """Close the per-job bar and log the completion summary."""
      if not self._job_bar:
         return
      self._job_bar.close()
      self._job_bar = None
      super().eval_done()

   def eval_status(self, new: bool | None, n: int = 1) -> None:
      """Forward status update to both the total bar and the per-job bar."""
      super().eval_status(new, n)
      if self._total_bar:
         self._total_bar.status(new)
      if self._job_bar:
         self._job_bar.status(new)
