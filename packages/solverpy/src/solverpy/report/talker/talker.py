"""
# Talker — evaluation progress interface

Base class for progress reporting during benchmark evaluation.
Subclasses receive lifecycle events (`begin`, `next`, `launching`, `finished`, `done`, `end`)
and decide how to surface them — as log messages ([`LogTalker`][solverpy.report.talker.logtalker.LogTalker]),
progress bars ([`EvalTalker`][solverpy.report.talker.evaltalker.EvalTalker]),
or forwarded across processes ([`RemoteTalker`][solverpy.report.talker.remotetalker.RemoteTalker]).

Also owns the log queue machinery that lets worker processes route Python
`logging` records back to the parent's handlers.
"""

from typing import Any, Sequence, TYPE_CHECKING
import logging
from queue import Queue
from logging.handlers import QueueHandler, QueueListener

from ...task.task import Task
from ...solver.object import SolverPyObj

if TYPE_CHECKING:
   from ...tools.typing import Result, SolverJob
   from ...task.solvertask import SolverTask  # TODO: generalize to Task

logger = logging.getLogger(__name__)


class Talker(SolverPyObj):
   """
   Abstract base for evaluation progress reporters.

   ```plantuml name="task-talker"
   class solverpy.report.talker.talker.Talker {
      - _log_queue: Queue[Any] | None
      - _listener: QueueListener | None

      --
      + {static} log_config(queue)
      + log_prepare()
      + log_start()
      + log_stop()
      + listening_start()
      + listening_stop()
      + begin(jobs, refjob, sidnames, **kwargs)
      + end(results, refjob)
      + next(job)
      + terminate()
      + launching(tasks)
      + finished(task, result)
      + done()
   }
   class solverpy.report.talker.logtalker.LogTalker extends solverpy.report.talker.talker.Talker
   class solverpy.report.talker.remotetalker.RemoteTalker extends solverpy.report.talker.talker.Talker
   ```

   Subclasses receive lifecycle events fired by the evaluation pipeline and
   decide how to surface them.  The base class is a silent no-op talker;
   every hook has a default no-op implementation so `Talker()` can be used
   as a drop-in "null" reporter wherever a talker is required.

   Also owns the cross-process log queue: `log_prepare` creates the queue,
   while `log_start` starts a `QueueListener` in the parent. Worker processes
   call `log_config` to redirect their root logger through the queue so records
   arrive at the parent's handlers.
   """

   def __init__(self):
      SolverPyObj.__init__(self)
      self._log_queue: Queue[Any] | None = None
      self._listener: QueueListener | None = None
      self._result: Any = None

   def represent(self) -> str:
      return type(self).__name__

   @staticmethod
   def log_config(queue: "Queue[Any] | None") -> None:
      """Configure child process logger to use the queue."""
      if not queue:
         return
      root = logging.getLogger()
      root.handlers.clear()
      for name in logging.root.manager.loggerDict:
         logging.getLogger(name).handlers.clear()
      root.addHandler(QueueHandler(queue))
      root.setLevel(logging.DEBUG)

   def log_start(self) -> None:
      """Start parent log-queue listener. No-op if queue not set or already started."""
      if self._log_queue is None or self._listener is not None:
         return
      root = logging.getLogger()
      self._listener = QueueListener(self._log_queue,
                                     *root.handlers,
                                     respect_handler_level=True)
      self._listener.start()

   def log_stop(self) -> None:
      """Stop parent log-queue listener."""
      if self._listener:
         self._listener.stop()
         self._listener = None

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
      """Called once before evaluation starts with the full list of jobs."""
      del jobs, refjob, sidnames, kwargs

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
      """Called after each evaluation job set completes."""
      pass

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

   def eval_status(self, new: "bool | None", n: int = 1) -> None:
      """Called when a task result is classified (True=solved, False=unsolved, None=error)."""
      del new, n

   def tune_begin(self, t_start: float, total: int = 0) -> None:
      """Hyperparameter tuning session starting; total trial count known."""
      del t_start, total

   def tune_end(self, t_end: float) -> None:
      """Tuning session finished."""
      del t_end

   def tune_result(self, val: Any) -> None:
      """Tuning produced a final result value."""
      self._result = val

   def tune_phase_begin(self, nick: str, iters: int,
                        timeout: "int | None") -> None:
      """A new tuning phase starting (e.g. ``"leaves"``)."""
      del nick, iters, timeout

   def tune_phase_done(self, nick: str) -> None:
      """A tuning phase finished."""
      del nick

   def tune_trial_begin(self, nick: str, it: int, values: "list[Any]") -> None:
      """An Optuna trial starting; parameter values being evaluated are known."""
      del nick, it, values

   def tune_trial_done(self, stats: "dict[str, Any]") -> None:
      """An Optuna trial finished; scores and accuracies are known."""
      del stats

   def tune_eval_begin(self) -> None:
      """ATP evaluation phase inside a tuning trial is starting."""

   def tune_eval_end(self, results: "dict") -> None:
      """ATP evaluation phase inside a tuning trial finished."""
      del results

   def build_begin(self, f_mod: str, total: int) -> None:
      """LightGBM model training starting; total iteration count known."""
      del f_mod, total

   def build_step(
      self,
      n: int,
      total: int,
      metrics: "dict[str, dict[str, float]]",
   ) -> None:
      """One LightGBM training iteration completed; labeled metrics are known."""
      del n, total, metrics

   def build_selected(
      self,
      iteration: int,
      metrics: "dict[str, dict[str, float]]",
   ) -> None:
      """The selected LightGBM iteration and its final metrics are known."""
      del iteration, metrics

   def build_done(self, score: float) -> None:
      """Model training finished; final ML score known."""
      del score

   def train_data(self, stats: "list[dict[str, Any]]") -> None:
      """Training-data files are ready; storage and sample statistics are known."""
      del stats

   def info(self, msg: str) -> None:
      """Log an info-level message."""
      del msg

   def debug(self, msg: str) -> None:
      """Log a debug-level message."""
      del msg
