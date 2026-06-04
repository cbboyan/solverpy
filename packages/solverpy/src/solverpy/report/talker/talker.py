"""
# Talker — evaluation progress interface

Base class for progress reporting during benchmark evaluation.
Subclasses receive lifecycle events (`begin`, `next`, `launching`, `finished`, `done`, `end`)
and decide how to surface them — as log messages ([`LogTalker`][solverpy.report.talker.logtalker.LogTalker]),
progress bars ([`SolverTalker`][solverpy.report.talker.solvertalker.SolverTalker]),
or forwarded across processes ([`RemoteTalker`][solverpy.report.talker.remotetalker.RemoteTalker]).

Also owns the log queue machinery that lets worker processes route Python
`logging` records back to the parent's handlers.
"""

from typing import Any, Sequence, TYPE_CHECKING
import logging
import multiprocessing as mp
from queue import Queue
from logging.handlers import QueueHandler, QueueListener

from ...task.task import Task

if TYPE_CHECKING:
   from ...tools.typing import Result, SolverJob
   from ...task.solvertask import SolverTask  # TODO: generalize to Task

logger = logging.getLogger(__name__)


class Talker:
   """
   Abstract base for evaluation progress reporters.

   ```plantuml name="task-talker"
   abstract class solverpy.report.talker.talker.Talker {
      - _log_queue: Queue[Any] | None
      - _listener: QueueListener | None
      - _manager: SyncManager | None
      --
      + {static} log_config(queue)
      + log_start()
      + log_stop()
      + listening_start()
      + listening_stop()
      + {abstract} begin(jobs, refjob, sidnames, **kwargs)
      + end(results, refjob)
      + next(job)
      + terminate()
      + launching(tasks)
      + finished(task, result)
      + done()
   }
   abstract class solverpy.report.talker.logtalker.LogTalker extends solverpy.report.talker.talker.Talker
   abstract class solverpy.report.talker.remotetalker.RemoteTalker extends solverpy.report.talker.talker.Talker
   ```

   Subclasses receive lifecycle events fired by the evaluation pipeline and
   decide how to surface them.  The base class provides no-op default
   implementations for all optional hooks, and raises `NotImplementedError`
   for `begin` which every concrete subclass must implement.

   Also owns the cross-process log queue: `log_start` creates a
   `QueueListener` in the parent; worker processes call `log_config` to
   redirect their root logger through the queue so records arrive at the
   parent's handlers.
   """

   def __init__(self):
      self._log_queue: Queue[Any] | None = None
      self._listener: QueueListener | None = None
      self._manager: mp.managers.SyncManager | None = None

   @staticmethod
   def log_config(queue: "Queue[Any] | None") -> None:
      """Configure child process logger to use the queue."""
      if not queue:
         return
      logger.debug("redirecting logger to the queue")
      root = logging.getLogger()
      root.handlers.clear()
      for name in logging.root.manager.loggerDict:
         logging.getLogger(name).handlers.clear()
      root.addHandler(QueueHandler(queue))
      root.setLevel(logging.DEBUG)
      logger.debug("logging redirected")

   def log_start(self) -> None:
      """Start parent logging from the queue."""
      root = logging.getLogger()
      self._manager = mp.get_context("forkserver").Manager()
      assert self._manager
      self._log_queue = self._manager.Queue()
      assert self._log_queue
      self._listener = QueueListener(self._log_queue, *root.handlers)
      self._listener.start()

   def log_stop(self) -> None:
      """Stop parent logging from the queue."""
      if self._listener:
         self._listener.stop()
         self._listener = None
      if self._manager:
         self._manager.shutdown()
         self._manager = None

   def listening_start(self) -> None:
      """Start the log queue listener. Subclasses extend this to start additional threads."""
      self.log_start()

   def listening_stop(self) -> None:
      """Stop the log queue listener. Subclasses extend this to stop additional threads."""
      self.log_stop()

   def eval_begin(
      self,
      jobs: list["SolverJob"],
      *,
      refjob: "SolverJob | None" = None,
      sidnames: bool = True,
      **kwargs,
   ) -> None:
      """
      Called once before evaluation starts with the full list of jobs.

      Args:
          jobs: all ``(solver, bid, sid)`` jobs that will be evaluated.
          refjob: the reference job for relative reporting, or ``None``.
          sidnames: if ``True``, use ``s1``/``s2`` style nick names.
      """
      del jobs, refjob, sidnames, kwargs
      raise NotImplementedError(
         "Talker.eval_begin: abstract method not implemented.")

   def eval_end(
      self,
      results: dict["SolverJob", "Result"],
      refjob: "SolverJob | None" = None,
   ) -> None:
      """
      Called once after all jobs complete. Calls `terminate` by default.

      Args:
          results: mapping from each job to its result dict.
          refjob: the reference job used for relative reporting.
      """
      del results, refjob
      self.terminate()

   def eval_next(self, job: "SolverJob") -> None:
      """Called when evaluation moves to the next job."""
      del job

   def terminate(self) -> None:
      """Clean up: stop the log queue listener."""
      self.log_stop()

   def eval_launch(self, tasks: Sequence["Task"]) -> None:
      """
      Called just before a batch of tasks is dispatched to worker processes.

      Injects the log queue into each task so workers can route their
      ``logging`` records back to the parent.
      """
      if self._log_queue is None:
         return
      for task in tasks:
         task.logqueue = self._log_queue

   def eval_taskdone(self, task: "SolverTask", result: "Result") -> None:
      """Called each time a single task completes."""
      del task, result

   def eval_done(self) -> None:
      """Called after all tasks in the current job have finished."""
      pass
