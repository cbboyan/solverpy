import logging
from typing import TYPE_CHECKING, Sequence

from .logtalker import LogTalker
from ..benchmark.path import bids as _bids
from .bar import SolvingBar, RunningBar, _postfix_width

if TYPE_CHECKING:
   from ..tools.typing import Result, SolverJob
   from .task import Task

logger = logging.getLogger(__name__)


class SolverTalker(LogTalker):

   def __init__(self) -> None:
      super().__init__(log_progress=False)
      self._job_bar: SolvingBar | None = None
      self._total_bar: RunningBar | None = None

   def begin(
      self,
      jobs: list["SolverJob"],
      *,
      refjob: "SolverJob | None" = None,
      sidnames: bool = True,
      miniters: int = 1,
      **kwargs,
   ) -> None:
      super().begin(jobs, refjob=refjob, sidnames=sidnames, **kwargs)
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

   def end(
      self,
      results: dict["SolverJob", "Result"],
      refjob: "SolverJob | None" = None,
   ) -> None:
      assert self._total_bar
      self._total_errors = self._total_bar._errors
      super().end(results, refjob=refjob)

   def terminate(self) -> None:
      super().terminate()
      if self._total_bar:
         self._total_bar.close()
         self._total_bar = None
      if self._job_bar:
         self._job_bar.close()
         self._job_bar = None

   def next(self, job: "SolverJob") -> None:
      super().next(job)

   def launching(self, tasks: Sequence["Task"]) -> None:
      super().launching(tasks)
      self._job_bar = SolvingBar(len(tasks), self._job_desc, miniters=1)

   def done(self) -> None:
      if not self._job_bar:
         return
      self._job_bar.close()
      self._job_bar = None
      super().done()

   def status(self, new: bool | None, n: int = 1) -> None:
      super().status(new, n)
      if self._total_bar:
         self._total_bar.status(new)
      if self._job_bar:
         self._job_bar.status(new)

