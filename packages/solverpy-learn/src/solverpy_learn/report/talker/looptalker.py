"""
# LoopTalker — progress reporter for hyperparameter tuning

Combines ATP evaluation progress (tqdm bars or log lines) and LightGBM
tuning progress into a single talker for
[`AutoTuner`][solverpy_learn.builder.autotuner.AutoTuner].

Runs entirely in the parent process; cross-process forwarding is handled by
[`RemoteTalker`][solverpy.report.talker.remotetalker.RemoteTalker] wrapping it.
"""

import logging
from typing import Any, Sequence, TYPE_CHECKING

from solverpy.report.talker.evaltalker import EvalTalker
from solverpy.report.talker.logtalker import LogTalker
from solverpy.report.talker.bar import BuilderBar, DefaultBar, RunningBar, _postfix_width
from solverpy.benchmark.path import bids as _bids

if TYPE_CHECKING:
   from solverpy.task.task import Task

logger = logging.getLogger(__name__)


class LoopTalker(EvalTalker):
   """
   Progress talker for the hyperparameter tuning pipeline.

   ```plantuml name="autotune-looptalker"
   abstract class solverpy.report.talker.talker.Talker
   class solverpy.report.talker.logtalker.LogTalker extends solverpy.report.talker.talker.Talker
   class solverpy.report.talker.evaltalker.EvalTalker extends solverpy.report.talker.logtalker.LogTalker
   class solverpy_learn.report.talker.looptalker.LoopTalker extends solverpy.report.talker.evaltalker.EvalTalker {
      - _tune_bar: DefaultBar | None
      - _builder_bar: BuilderBar | None
      - _total_trials: int
      - _current_trial: int
      - _in_tuning: bool
      - _in_optuna_trial: bool
      --
      + eval_begin(jobs, *, refjob, sidnames, miniters, **kwargs)
      + eval_end(results, refjob, **kwargs)
      + eval_launch(tasks)
      + eval_done()
      + tune_begin(t_start, total)
      + tune_end(t_end)
      + tune_trial_begin(nick, it, values)
      + tune_trial_done(stats)
      + build_begin(f_mod, total)
      + build_step(n, total, metrics)
      + build_selected(iteration, metrics)
      + build_done(score)
   }
   ```

   Outside a tuning phase, behaves identically to
   [`EvalTalker`][solverpy.report.talker.evaltalker.EvalTalker] (per-job
   ``SolvingBar`` + cumulative ``RunningBar``).

   Inside a tuning phase (between ``tune_begin`` / ``tune_end``), switches to
   two-bar tuning mode: an outer ``tune`` bar counting completed trials, and
   an inner ``[N/M] build`` or ``[N/M] eval`` bar for the current LightGBM
   training or ATP evaluation.  All desc strings are padded to the same width
   for alignment.

   Set ``headless=True`` for non-interactive use: all handlers use
   ``logger.info`` and no tqdm bars are created.
   """

   def __init__(self, headless: bool = False) -> None:
      """
      Args:
          headless: if ``True``, use log lines instead of tqdm bars.
      """
      super().__init__(headless=headless)
      self._builder_bar: BuilderBar | None = None
      self._tune_bar: DefaultBar | None = None
      self._total_trials: int = 0
      self._current_trial: int = 0
      self._in_tuning: bool = False
      self._in_optuna_trial: bool = False
      self._in_tune_eval: bool = False

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

   def eval_begin(self,
                  jobs,
                  *,
                  refjob=None,
                  sidnames=True,
                  miniters=1,
                  **kwargs) -> None:
      """Outside tuning: full EvalTalker bars. Inside tuning: single RunningBar, skips report."""
      if not self._in_tuning:
         EvalTalker.eval_begin(self,
                               jobs,
                               refjob=refjob,
                               sidnames=sidnames,
                               miniters=miniters,
                               **kwargs)
         return
      LogTalker.eval_begin(self,
                           jobs,
                           refjob=refjob,
                           sidnames=sidnames,
                           report=False,
                           **kwargs)
      if not self._headless:
         max_job = max(len(_bids.problems(bid)) for (_, bid, _) in jobs)
         self._total_bar = RunningBar(
            total=self._total_count,
            desc=self._trial_desc("eval "),
            miniters=miniters,
            colour="blue",
            leave=True,
            postfix_width=_postfix_width(max_job),
         )

   def eval_end(self, results, refjob=None, **kwargs) -> None:
      """Outside tuning: full EvalTalker end. Inside tuning: close eval bar, update tune bar."""
      if not self._in_tuning:
         EvalTalker.eval_end(self, results, refjob=refjob, **kwargs)
         return
      if self._total_bar:
         self._total_errors = self._total_bar._errors
         self._total_bar.close()
         self._total_bar = None
      LogTalker.eval_end(self, results, refjob=refjob, report=False)
      if not self._in_optuna_trial:
         self._current_trial += 1
         if self._tune_bar:
            self._tune_bar.update(1)

   def eval_status(self, new: "bool | None", n: int = 1) -> None:
      """Update eval bar and refresh tune bar to keep it visible."""
      super().eval_status(new, n)
      if self._tune_bar:
         self._tune_bar.refresh()

   def eval_launch(self, tasks: Sequence["Task"]) -> None:
      """Outside tuning: per-job SolvingBar. Inside tuning: record time only."""
      if not self._in_tuning:
         EvalTalker.eval_launch(self, tasks)
      else:
         LogTalker.eval_launch(self, tasks)

   def eval_done(self) -> None:
      """Outside tuning: close job bar. Inside tuning: log without closing any bar."""
      if not self._in_tuning:
         EvalTalker.eval_done(self)
      else:
         LogTalker.eval_done(self)

   # --- Tuning lifecycle overrides ---

   def tune_begin(self, t_start: float, total: int = 0) -> None:
      """Enter tuning mode; create outer tune bar if not headless."""
      self._in_tuning = True
      self._total_trials = total
      self._current_trial = 0
      self._suspend_info = not self._headless
      if self._headless or not total:
         return
      self._tune_bar = DefaultBar(total, "tune".ljust(self._inner_width()))

   def tune_end(self, t_end: float) -> None:
      """Leave tuning mode; close tune bar and restore info logs."""
      self._in_tuning = False
      self._suspend_info = False
      self._total_trials = 0
      self._current_trial = 0
      if self._tune_bar:
         self._tune_bar.close()
         self._tune_bar = None

   def tune_trial_begin(self, nick: str, it: int, values: list) -> None:
      """Mark start of Optuna trial and delegate to LogTalker."""
      self._in_optuna_trial = True
      LogTalker.tune_trial_begin(self, nick, it, values)

   def tune_trial_done(self, stats: dict[str, Any]) -> None:
      """Increment tune bar at end of Optuna trial."""
      LogTalker.tune_trial_done(self, stats)
      self._in_optuna_trial = False
      self._current_trial += 1
      if self._tune_bar:
         self._tune_bar.update(1)

   def tune_eval_begin(self) -> None:
      """Suppress eval log messages while ATP evaluation runs inside a tuning trial."""
      self._in_tune_eval = True

   def tune_eval_end(self, results: dict) -> None:
      """Re-enable eval log messages after tuning ATP evaluation."""
      self._in_tune_eval = False

   def terminate(self) -> None:
      """Delegate to parent; _tune_bar is closed by tune_end()."""
      super().terminate()

   # --- Model build overrides ---

   def build_begin(self, f_mod: str, total: int) -> None:
      """Open a ``BuilderBar`` with [N/M] build label if not headless."""
      LogTalker.build_begin(self, f_mod, total)
      if not self._headless:
         self._builder_bar = BuilderBar(total,
                                        self._trial_desc("build"),
                                        colour="blue",
                                        leave=True)

   def build_step(
      self,
      n: int,
      total: int,
      metrics: dict[str, dict[str, float]],
   ) -> None:
      """Update the builder bar, refresh tune bar, and emit periodic log lines."""
      if self._builder_bar:
         self._builder_bar.status(metrics)
      if self._tune_bar:
         self._tune_bar.refresh()
      LogTalker.build_step(self, n, total, metrics)

   def build_selected(
      self,
      iteration: int,
      metrics: dict[str, dict[str, float]],
   ) -> None:
      """Report selected-model metrics through the log/reporting layer."""
      LogTalker.build_selected(self, iteration, metrics)

   def build_done(self, score: float) -> None:
      """Close the builder bar."""
      if self._builder_bar:
         self._builder_bar.close()
         self._builder_bar = None
      LogTalker.build_done(self, score)
