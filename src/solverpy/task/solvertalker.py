import logging
from typing import TYPE_CHECKING, Sequence

from .logtalker import LogTalker, jobname
from .bar import SolvingBar, RunningBar

if TYPE_CHECKING:
   from ..tools.typing import Result, SolverJob
   from .task import Task
   from .solvertask import SolverTask

logger = logging.getLogger(__name__)


class SolverTalker(LogTalker):

   def __init__(self):
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
   ):
      super().begin(jobs, refjob=refjob, sidnames=sidnames, **kwargs)
      self._total_bar = RunningBar(
         total=self._total_count,
         desc=self._total_desc,
         miniters=miniters,
      )

   def end(
      self,
      results: dict["SolverJob", "Result"],
      refjob: "SolverJob | None" = None,
   ):
      assert self._total_bar
      self._total_errors = self._total_bar._errors
      super().end(results, refjob=refjob)

   def terminate(self):
      super().terminate()
      if self._total_bar:
         self._total_bar.close()
         self._total_bar = None
      if self._job_bar:
         self._job_bar.close()
         self._job_bar = None

   def next(self, job: "SolverJob"):
      super().next(job)

   def launching(self, tasks: Sequence["Task"]):
      super().launching(tasks)
      self._job_bar = SolvingBar(len(tasks), self._job_desc, miniters=1)

   def done(self):
      if not self._job_bar:
         return
      self._job_bar.close()
      self._job_bar = None
      super().done()

   def status(self, new: bool | None, n: int = 1):
      super().status(new, n)
      if self._total_bar:
         self._total_bar.status(new)
      if self._job_bar:
         self._job_bar.status(new)

