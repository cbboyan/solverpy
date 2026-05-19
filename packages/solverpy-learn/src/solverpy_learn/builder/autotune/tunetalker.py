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
from solverpy.talker.bar import BuilderBar, DefaultBar, RunningBar, _postfix_width
from solverpy.benchmark.path import bids as _bids

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
      - _tune_bar: DefaultBar | None
      - _total_trials: int
      - _current_trial: int
      - _in_optuna_trial: bool
      --
      + listening_start()
      + listening_stop()
      + wait() : Any
      + result(val)
      + tuning(t_start, total)
      + tuned(t_end)
      + trying(nick, it, values)
      + tried(stats)
      + building(f_mod, total)
      + iteration(n, total, loss)
      + built(score)
   }
   ```

   Two tqdm bars are shown at any time: an outer ``tune`` bar counting
   completed trials, and an inner ``[N/M] build`` or ``[N/M] eval `` bar
   showing progress of the current LightGBM training or ATP evaluation.
   All desc strings are padded to the same width for alignment.

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
      self._tune_bar: DefaultBar | None = None
      self._total_trials: int = 0
      self._current_trial: int = 0
      self._in_optuna_trial: bool = False

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

   def terminate(self) -> None:
      """Close tune bar then delegate to parent."""
      if self._tune_bar:
         self._tune_bar.close()
         self._tune_bar = None
      super().terminate()

   # --- Helpers ---

   def _trial_desc(self, name: str) -> str:
      """Return '[N/M] name' aligned with the tune bar, or just 'name' if total unknown."""
      if not self._total_trials:
         return name
      dw = len(str(self._total_trials))
      n = self._current_trial + 1
      return f"[{n:>{dw}}/{self._total_trials}] {name}"

   def _inner_width(self) -> int:
      """Width of '[N/M] build' / '[N/M] eval ' for tune bar desc alignment."""
      if not self._total_trials:
         return 0
      dw = len(str(self._total_trials))
      return 2 * dw + 9  # len("[N/M] build") with dw-wide fields

   # --- ATP evaluation overrides ---

   def begin(self, jobs, *, refjob=None, sidnames=True, miniters=1, **kwargs) -> None:
      """Create a single cumulative eval RunningBar if not headless. Skips report."""
      LogTalker.begin(self, jobs, refjob=refjob, sidnames=sidnames, report=False, **kwargs)
      if not self._log_progress:
         max_job = max(len(_bids.problems(bid)) for (_, bid, _) in jobs)
         self._total_bar = RunningBar(
            total=self._total_count,
            desc=self._trial_desc("eval "),
            miniters=miniters,
            postfix_width=_postfix_width(max_job),
         )

   def end(self, results, refjob=None, **kwargs) -> None:
      """Close eval bar, update tune bar for init model, skip report."""
      if self._total_bar:
         self._total_errors = self._total_bar._errors
         self._total_bar.close()
         self._total_bar = None
      LogTalker.end(self, results, refjob=refjob, report=False)
      if not self._in_optuna_trial:
         self._current_trial += 1
         if self._tune_bar:
            self._tune_bar.update(1)

   def launching(self, tasks: Sequence["Task"]) -> None:
      """Record start time only; no per-job bar in tuning mode."""
      LogTalker.launching(self, tasks)

   def done(self) -> None:
      """Log job completion without closing any bar."""
      LogTalker.done(self)

   # --- Tuning lifecycle overrides ---

   def tuning(self, t_start: float, total: int = 0) -> None:
      """Create the outer tune bar if not headless."""
      self._total_trials = total
      self._current_trial = 0
      if self._log_progress or not total:
         return
      self._tune_bar = DefaultBar(total, "tune".ljust(self._inner_width()))

   def tuned(self, t_end: float) -> None:
      """Close the tune bar on tuning completion."""
      if self._tune_bar:
         self._tune_bar.close()
         self._tune_bar = None

   def trying(self, nick: str, it: int, values: list) -> None:
      """Mark start of Optuna trial and delegate to LogTalker."""
      self._in_optuna_trial = True
      LogTalker.trying(self, nick, it, values)

   def tried(self, stats: dict[str, Any]) -> None:
      """Increment tune bar at end of Optuna trial."""
      LogTalker.tried(self, stats)
      self._in_optuna_trial = False
      self._current_trial += 1
      if self._tune_bar:
         self._tune_bar.update(1)

   def result(self, val: Any) -> None:
      """Store the tuning result and unblock ``wait()``."""
      self._result = val
      self._result_event.set()

   # --- Model build overrides ---

   def building(self, f_mod: str, total: int) -> None:
      """Open a ``BuilderBar`` with [N/M] build label if not headless."""
      LogTalker.building(self, f_mod, total)
      if not self._log_progress:
         self._builder_bar = BuilderBar(total, self._trial_desc("build"))

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
