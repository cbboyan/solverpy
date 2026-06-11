
# Talker Methods

## Method summary

### Evaluation lifecycle

| Method | Description |
|---|---|
| `eval_begin(jobs, refjob, sidnames)` | Evaluation is starting; full job list is known. Set up counters, bars, report header. |
| `eval_end(results, refjob)` | All jobs finished normally. Write summary, close bars, clean up. |
| `terminate()` | Abort in progress (keyboard interrupt or exception). Close bars, stop queues. |
| `eval_next(job)` | Moving to the next `(solver, bid, sid)` job. Reset per-job state. |
| `eval_launch(tasks)` | A batch of tasks is about to be dispatched to the worker pool. |
| `eval_taskdone(task, result)` | A single task completed (cached or live). Update progress. |
| `eval_done()` | All tasks in the current job finished. Log/display per-job summary. |
| `eval_status(new, n)` | One task result classified: `True` = solved, `False` = unsolved, `None` = error. |

### Tuning lifecycle

| Method | Description |
|---|---|
| `tune_begin(t_start, total)` | Hyperparameter tuning session starting; total trial count known. |
| `tune_end(t_end)` | Tuning session finished. Close outer progress bar. |
| `tune_phase_begin(nick, iters, timeout)` | A new tuning phase starting (e.g. `"leaves"`). |
| `tune_trial_begin(nick, it, values)` | An Optuna trial starting; parameter values being evaluated are known. |
| `tune_trial_done(stats)` | An Optuna trial finished; scores and accuracies are known. |
| `tune_phase_done(nick)` | A tuning phase finished; write phase results table to report. |
| `build_begin(f_mod, total)` | LightGBM model training starting; total iteration count known. |
| `build_step(n, total, metrics)` | One LightGBM training iteration completed; labeled metrics by dataset are known. |
| `build_selected(iteration, metrics)` | The selected LightGBM iteration and its final threshold metrics are known. |
| `build_done(score)` | Model training finished; final ML score known. |
| `tune_result(val)` | Tuning produced a final result tuple; unblocks the parent `wait()`. |

### Logging helpers

| Method | Description |
|---|---|
| `info(msg)` | Log an info-level message from the child process. |
| `debug(msg)` | Log a debug-level message from the child process (currently a no-op). |

---

## Implementation per talker

### Evaluation lifecycle

| Method | Talker | LogTalker | SolverTalker | TuneTalker |
|---|---|---|---|---|
| `eval_begin(jobs, refjob, sidnames)` | abstract | counters, legend, log | + RunningBar (green) | + RunningBar (blue, leave=False), no report |
| `eval_end(results, refjob)` | → `terminate()` | log summary, report | harvest errors | close eval bar, update tune bar, no report |
| `terminate()` | `log_stop()` | — | close both bars | skip (_tune_bar owned by `tune_end()`) |
| `eval_next(job)` | no-op | reset counters, log | — | — |
| `eval_launch(tasks)` | inject log queue | record start time | + SolvingBar (blue) | skip bar, LogTalker only |
| `eval_taskdone(task, result)` | no-op | → `eval_status()` | — | — |
| `eval_done()` | no-op | log job summary | close SolvingBar | LogTalker only (no bar) |
| `eval_status(new, n)` | — | counters + periodic log | + update both bars | — |

### Tuning lifecycle

| Method | LogTalker | TuneTalker |
|---|---|---|
| `tune_begin(t_start, total)` | no-op | create tune bar (green) |
| `tune_end(t_end)` | no-op | close tune bar |
| `tune_phase_begin(nick, iters, timeout)` | report heading, reset table | inherited |
| `tune_trial_begin(nick, it, values)` | record desc, log if verbose | + set `_in_optuna_trial=True` |
| `tune_trial_done(stats)` | append to table | + clear flag, increment, update tune bar |
| `tune_phase_done(nick)` | write table to report, log | inherited |
| `build_begin(f_mod, total)` | log start | + create BuilderBar (blue, leave=False) |
| `build_step(n, total, metrics)` | periodic log | + update BuilderBar |
| `build_selected(iteration, metrics)` | selected metrics log | inherited |
| `build_done(score)` | log debug | + close BuilderBar |
| `tune_result(val)` | store `_result` | + set `_result_event` (unblocks `tune_wait()`) |

### Logging helpers

| Method | LogTalker | TuneTalker |
|---|---|---|
| `info(msg)` | `logger.info` | inherited (queued in child) |
| `debug(msg)` | no-op | inherited (queued in child) |

---

## Call sites

For each method: where it is called, from which file, and with what arguments.

---

## Evaluation lifecycle

### `eval_begin(jobs, refjob, sidnames)`

| Caller | File | Args |
|---|---|---|
| `evaluation.launch()` → `initialize_jobs()` | `benchmark/evaluation.py:201` | `jobs` (all `(solver,bid,sid)` combos), `refjob=refjob`, `sidnames=sidnames` |

---

### `eval_end(results, refjob)`

| Caller | File | Args |
|---|---|---|
| `evaluation.launch()` → `launch_jobs()` | `benchmark/evaluation.py:216` | `allres` (full result dict), `refjob=refjob` |

---

### `terminate()`

| Caller | File | Context |
|---|---|---|
| `Talker.eval_end()` | `report/talker/talker.py:146` | Called at end of normal evaluation |
| `evaluation.launch()` → `launch_jobs()` | `benchmark/evaluation.py:218` | `KeyboardInterrupt` handler |
| `task/launcher.launch()` | `task/launcher.py:76` | `KeyboardInterrupt` handler inside pool |
| `prettytuner()` | `builder/autotune/autotune.py:155` | Exception handler around child process |

---

### `eval_next(job)`

| Caller | File | Args |
|---|---|---|
| `evaluation.run()` | `benchmark/evaluation.py:52` | `job` = `(solver, bid, sid)` |

---

### `eval_launch(tasks)`

| Caller | File | Args |
|---|---|---|
| `task/launcher.launch()` | `task/launcher.py:57` | `tasks` = list of `SolverTask` |

---

### `eval_taskdone(task, result)`

| Caller | File | Args |
|---|---|---|
| `evaluation.run()` → `restrict_problems()` | `benchmark/evaluation.py:76` | `SolverTask(solver,bid,sid,problem)`, simulated timeout result (skipped problems) |
| `evaluation.run()` → `check_cache()` | `benchmark/evaluation.py:120` | `task` (cached `SolverTask`), cached `result` |
| `task/launcher.launch()` | `task/launcher.py:68` | `tids[tid]` (`SolverTask`), `result` from worker |

---

### `eval_done()`

| Caller | File | Context |
|---|---|---|
| `task/launcher.launch()` | `task/launcher.py:83` | `finally` block after pool completes or raises |

---

### `eval_status(new, n)`

| Caller | File | Args |
|---|---|---|
| `LogTalker.eval_taskdone()` | `report/talker/logtalker.py:169` | `task.status(result)` → `True`/`False`/`None` |

---

## Tuning lifecycle

### `tune_begin(t_start, total)`

| Caller | File | Args |
|---|---|---|
| `tuner()` | `builder/autotune/autotune.py:66` | `time.time()`, `_total` (= `n_phases * iters_per_phase + (1 if init_params else 0)`) |

---

### `tune_end(t_end)`

| Caller | File | Args |
|---|---|---|
| `tuner()` | `builder/autotune/autotune.py:129` | `time.time()` |

---

### `tune_phase_begin(nick, iters, timeout)`

| Caller | File | Args |
|---|---|---|
| `tune.tune()` | `builder/autotune/tune.py:28` | `nick` (phase name e.g. `"leaves"`), `iters` (per-phase count), `timeout` (per-phase seconds or `None`) |

---

### `tune_trial_begin(nick, it, values)`

| Caller | File | Args |
|---|---|---|
| `check.leaves()` | `builder/autotune/check.py:49` | `"leaves"`, `trial.number`, `(num_leaves,)` |
| `check.bagging()` | `builder/autotune/check.py:64` | `"bagging"`, `trial.number`, `(bagging_freq, bagging_fraction)` |
| `check.min_data()` | `builder/autotune/check.py:77` | `"min_data"`, `trial.number`, `(min_data,)` |
| `check.regular()` | `builder/autotune/check.py:91` | `"regular"`, `trial.number`, `(lambda_l1, lambda_l2)` |
| `check.depth()` | `builder/autotune/check.py:104` | `"depth"`, `trial.number`, `(max_depth,)` |
| `check.learning_rate()` | `builder/autotune/check.py:117` | `"learning_rate"`, `trial.number`, `(learning_rate,)` |
| `check.posneg_weight()` | `builder/autotune/check.py:132` | `"posneg"`, `trial.number`, `(spw / posneg_base,)` |

---

### `tune_trial_done(stats)`

| Caller | File | Args |
|---|---|---|
| `check.check()` | `builder/autotune/check.py:35` | `stats` dict with keys: `score`, `mlscore`, `valid_acc` (3-tuple), `train_acc` (3-tuple), `duration` |

---

### `tune_phase_done(nick)`

| Caller | File | Args |
|---|---|---|
| `tune.tune()` | `builder/autotune/tune.py:39` | `nick` (phase name, same as passed to `tune_phase_begin()`) |

---

### `build_begin(f_mod, total)`

| Caller | File | Args |
|---|---|---|
| `build.model()` → `build_model()` via `report()` | `builder/autotune/build.py:82` | `f_mod` (path to model file), `params["num_round"]` (total LightGBM iterations) |

---

### `build_step(n, total, metrics)`

| Caller | File | Args |
|---|---|---|
| `build.model()` → `iteration_callback()` via `report()` | `builder/autotune/build.py` | 1-based iteration, total steps, nested dataset/metric/value mapping from `env.evaluation_result_list` |

---

### `build_selected(iteration, metrics)`

| Caller | File | Args |
|---|---|---|
| `build.model()` → `check_model()` via `report()` | `builder/autotune/build.py` | selected iteration and train/valid overall, positive, and negative threshold accuracy |

---

### `build_done(score)`

| Caller | File | Args |
|---|---|---|
| `build.model()` → `check_model()` via `report()` | `builder/autotune/build.py:110` | `mlscore` = `POS_ACC_WEIGHT * acc[1] + acc[2]` |

---

### `tune_result(val)`

| Caller | File | Args |
|---|---|---|
| `tuner()` | `builder/autotune/autotune.py:132` | `ret` = `(score, acc, trainacc, f_mod, duration, params, pos, neg)` |

---

## Logging helpers

### `info(msg)` / `debug(msg)`

| Caller | File | Args |
|---|---|---|
| `build.model()` via `report()` | `builder/autotune/build.py:57,74,92` | Debug strings (results list, early-stopping config, best iteration) |

These are only queued through the `TuneTalker` queue in the child process; in the parent they resolve to `logger.info` / no-op respectively.
