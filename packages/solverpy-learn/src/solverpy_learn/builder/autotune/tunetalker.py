"""
# TuneTalker — unified progress reporter for hyperparameter tuning

Combines ATP evaluation progress (tqdm bars or log lines) and LightGBM
tuning progress into a single self-contained talker for
[`AutoTuner`][solverpy_learn.builder.autotuner.AutoTuner].

The tuner child process (forked by
[`prettytuner`][solverpy_learn.builder.autotune.autotune.prettytuner]) calls
methods on its inherited copy of `TuneTalker`.  Methods listed in `REMOTES`
are intercepted by `__getattribute__` and put on a plain
`multiprocessing.Queue`; a background listening thread in the parent
dequeues them and dispatches to the real handlers.

Replaces the former `RemoteTalker(SolverTalker()) + AutotuneListener` pair.
"""

import logging
import multiprocessing
import threading
from typing import Any, Sequence, TYPE_CHECKING

from solverpy.talker.solvertalker import SolverTalker
from solverpy.talker.logtalker import LogTalker
from solverpy.talker.bar import BuilderBar

if TYPE_CHECKING:
   from solverpy.talker.task import Task

logger = logging.getLogger(__name__)


class TuneTalker(SolverTalker):
   """
   Self-contained progress talker for the hyperparameter tuning pipeline.

   ```plantuml name="autotune-tunetalker"
   abstract class solverpy.talker.talker.Talker
   class solverpy.talker.logtalker.LogTalker extends solverpy.talker.talker.Talker
   class solverpy.talker.solvertalker.SolverTalker extends solverpy.talker.logtalker.LogTalker
   class solverpy_learn.builder.autotune.tunetalker.TuneTalker extends solverpy.talker.solvertalker.SolverTalker {
      + REMOTES: set[str]
      - _queue: Queue
      - _listening_thread: Thread | None
      - _result_event: Event
      --
      + listening_start()
      + listening_stop()
      + wait() : Any
      + result(val)
      + building(f_mod, total)
      + iteration(n, total, loss)
      + built(score)
   }
   ```

   Methods in `REMOTES` are intercepted by `__getattribute__` in the child
   and queued; the parent's listening thread dispatches them to the real
   handlers.  ATP evaluation events and tuning events share one queue and
   thread.

   Log-based defaults for all tuning events (`trials`, `trying`, `tried`,
   `trialed`, etc.) are inherited from
   [`LogTalker`][solverpy.talker.logtalker.LogTalker].  In non-headless mode,
   `TuneTalker` overrides the model-building handlers to use a
   [`BuilderBar`][solverpy.talker.bar.BuilderBar] instead.

   Set ``headless=True`` for non-interactive use: all tuning handlers use
   ``logger.info`` and no tqdm bars are created.
   """

   REMOTES = {
      # ATP evaluation lifecycle (called from evaluation.launch in child)
      "begin", "end", "next", "launching", "finished", "done",
      # LightGBM model building (called from build.py in child)
      "building", "iteration", "built",
      # Optuna phase events (called from tune.py / check.py in child)
      "trials", "trying", "tried", "trialed",
      # Tuning lifecycle (called from tuner() in child)
      "tuning", "tuned", "result",
      # Logging helpers
      "info", "debug",
   }
   """Methods intercepted in the child and forwarded to the parent via queue."""

   def __init__(self, headless: bool = False) -> None:
      """
      Args:
          headless: if ``True``, use log lines instead of tqdm bars.
      """
      super().__init__()
      self._log_progress = headless  # override SolverTalker's False
      self._queue: multiprocessing.Queue = multiprocessing.Queue()
      self._listening_thread: threading.Thread | None = None
      self._stop_event: threading.Event = threading.Event()
      self._result_event: threading.Event = threading.Event()
      self._builder_bar: BuilderBar | None = None

   def __getattribute__(self, name: str):
      if name in TuneTalker.REMOTES:
         def wrapper(*args, **kwargs):
            queue = object.__getattribute__(self, '_queue')
            queue.put((name, args, kwargs))
         return wrapper
      return super().__getattribute__(name)

   # --- Listening thread ---

   def listening_start(self) -> None:
      """Start the listening thread. No log queue Manager is started."""
      self._stop_event.clear()
      self._listening_thread = threading.Thread(
         target=self._listen_loop,
         daemon=True,
      )
      self._listening_thread.start()

   def listening_stop(self) -> None:
      """Signal the listening thread to stop and wait for it to join."""
      if not (self._listening_thread and self._listening_thread.is_alive()):
         return
      self._stop_event.set()
      self._listening_thread.join(timeout=2.0)
      self._listening_thread = None

   def _listen_loop(self) -> None:
      """Drain the queue and dispatch each message to the real handler."""
      while not self._stop_event.is_set():
         try:
            (name, args, kwargs) = self._queue.get(timeout=0.2)
            self._dispatch(name, args, kwargs)
         except:
            pass

   def _dispatch(self, name: str, args: tuple, kwargs: dict) -> None:
      """Call the actual handler method, bypassing ``__getattribute__``."""
      try:
         handler = object.__getattribute__(self, name)
         handler(*args, **kwargs)
      except Exception as e:
         logger.error(f"Error dispatching {name}: {e}", exc_info=True)

   def wait(self) -> Any:
      """Block until the child sends a ``result`` message and return it."""
      self._result_event.wait()
      return self._result

   # --- ATP evaluation overrides ---

   def begin(self, jobs, *, refjob=None, sidnames=True, miniters=1, **kwargs) -> None:
      """Create the total ``RunningBar`` if not headless, else log only. Skips Evaluation/Legend report."""
      if self._log_progress:
         LogTalker.begin(self, jobs, refjob=refjob, sidnames=sidnames, report=False, **kwargs)
      else:
         super().begin(jobs, refjob=refjob, sidnames=sidnames, miniters=miniters, report=False, **kwargs)

   def end(self, results, refjob=None, **kwargs) -> None:
      """Delegate to parent but skip Summary/Statuses report sections."""
      super().end(results, refjob=refjob, report=False, **kwargs)

   def launching(self, tasks: Sequence["Task"]) -> None:
      """Record start time and create the per-job bar if not headless.

      Worker log queues are intentionally not injected here.
      To enable worker logging: call ``self.log_start()`` in ``listening_start()``
      and inject ``self._log_queue`` into each task.
      """
      LogTalker.launching(self, tasks)
      if not self._log_progress:
         from solverpy.talker.bar import SolvingBar
         self._job_bar = SolvingBar(len(tasks), self._job_desc, miniters=1)

   # --- Tuning event overrides (bars when not headless) ---

   def result(self, val: Any) -> None:
      """Store the tuning result and unblock ``wait()``."""
      self._result = val
      self._result_event.set()

   def building(self, f_mod: str, total: int) -> None:
      """Open a ``BuilderBar`` if not headless, else delegate to ``LogTalker``."""
      LogTalker.building(self, f_mod, total)
      if not self._log_progress:
         self._builder_bar = BuilderBar(total, self._tune_desc)

   def iteration(self, n: int, total: int, loss: list[float]) -> None:
      """Update the builder bar and emit periodic log lines."""
      if self._builder_bar:
         self._builder_bar.status(loss)
      LogTalker.iteration(self, n, total, loss)

   def built(self, score: float) -> None:
      """Close the builder bar."""
      if self._builder_bar:
         self._builder_bar.close()
         self._builder_bar = None
      LogTalker.built(self, score)
