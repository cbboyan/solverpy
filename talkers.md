# Talker Methods

## Method summary

### Evaluation lifecycle

| Method | Description |
|---|---|
| `begin(jobs, refjob, sidnames)` | Evaluation is starting; full job list is known. Set up counters, bars, report header. |
| `end(results, refjob)` | All jobs finished normally. Write summary, close bars, clean up. |
| `terminate()` | Abort in progress (keyboard interrupt or exception). Close bars, stop queues. |
| `next(job)` | Moving to the next `(solver, bid, sid)` job. Reset per-job state. |
| `launching(tasks)` | A batch of tasks is about to be dispatched to the worker pool. |
| `finished(task, result)` | A single task completed (cached or live). Update progress. |
| `done()` | All tasks in the current job finished. Log/display per-job summary. |
| `status(new, n)` | One task result classified: `True` = solved, `False` = unsolved, `None` = error. |

### Tuning lifecycle

| Method | Description |
|---|---|
| `tuning(t_start, total)` | Hyperparameter tuning session starting; total trial count known. |
| `tuned(t_end)` | Tuning session finished. Close outer progress bar. |
| `trials(nick, iters, timeout)` | A new tuning phase starting (e.g. `"leaves"`). |
| `trying(nick, it, values)` | An Optuna trial starting; parameter values being evaluated are known. |
| `tried(stats)` | An Optuna trial finished; scores and accuracies are known. |
| `trialed(nick)` | A tuning phase finished; write phase results table to report. |
| `building(f_mod, total)` | LightGBM model training starting; total iteration count known. |
| `iteration(n, total, loss)` | One LightGBM training iteration completed; current loss values known. |
| `built(score)` | Model training finished; final ML score known. |
| `result(val)` | Tuning produced a final result tuple; unblocks the parent `wait()`. |

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
| `begin(jobs, refjob, sidnames)` | abstract | counters, legend, log | + RunningBar (green) | + RunningBar (blue, leave=False), no report |
| `end(results, refjob)` | → `terminate()` | log summary, report | harvest errors | close eval bar, update tune bar, no report |
| `terminate()` | `log_stop()` | — | close both bars | skip (_tune_bar owned by `tuned()`) |
| `next(job)` | no-op | reset counters, log | — | — |
| `launching(tasks)` | inject log queue | record start time | + SolvingBar (blue) | skip bar, LogTalker only |
| `finished(task, result)` | no-op | → `status()` | — | — |
| `done()` | no-op | log job summary | close SolvingBar | LogTalker only (no bar) |
| `status(new, n)` | — | counters + periodic log | + update both bars | — |

### Tuning lifecycle

| Method | LogTalker | TuneTalker |
|---|---|---|
| `tuning(t_start, total)` | no-op | create tune bar (green) |
| `tuned(t_end)` | no-op | close tune bar |
| `trials(nick, iters, timeout)` | report heading, reset table | inherited |
| `trying(nick, it, values)` | record desc, log if verbose | + set `_in_optuna_trial=True` |
| `tried(stats)` | append to table | + clear flag, increment, update tune bar |
| `trialed(nick)` | write table to report, log | inherited |
| `building(f_mod, total)` | log start | + create BuilderBar (blue, leave=False) |
| `iteration(n, total, loss)` | periodic log | + update BuilderBar |
| `built(score)` | log debug | + close BuilderBar |
| `result(val)` | store `_result` | + set `_result_event` (unblocks `wait()`) |

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

### `begin(jobs, refjob, sidnames)`

| Caller | File | Args |
|---|---|---|
| `evaluation.launch()` → `initialize_jobs()` | `benchmark/evaluation.py:201` | `jobs` (all `(solver,bid,sid)` combos), `refjob=refjob`, `sidnames=sidnames` |

---

### `end(results, refjob)`

| Caller | File | Args |
|---|---|---|
| `evaluation.launch()` → `launch_jobs()` | `benchmark/evaluation.py:216` | `allres` (full result dict), `refjob=refjob` |

---

### `terminate()`

| Caller | File | Context |
|---|---|---|
| `Talker.end()` | `report/talker/talker.py:146` | Called at end of normal evaluation |
| `evaluation.launch()` → `launch_jobs()` | `benchmark/evaluation.py:218` | `KeyboardInterrupt` handler |
| `task/launcher.launch()` | `task/launcher.py:76` | `KeyboardInterrupt` handler inside pool |
| `prettytuner()` | `builder/autotune/autotune.py:157` | Exception handler around child process |
| `AutoTuner.tune()` | `builder/autotuner.py:101` | `KeyboardInterrupt` handler around `prettytuner()` |

---

### `next(job)`

| Caller | File | Args |
|---|---|---|
| `evaluation.run()` | `benchmark/evaluation.py:52` | `job` = `(solver, bid, sid)` |

---

### `launching(tasks)`

| Caller | File | Args |
|---|---|---|
| `task/launcher.launch()` | `task/launcher.py:57` | `tasks` = list of `SolverTask` |

---

### `finished(task, result)`

| Caller | File | Args |
|---|---|---|
| `evaluation.run()` → `restrict_problems()` | `benchmark/evaluation.py:76` | `SolverTask(solver,bid,sid,problem)`, simulated timeout result (skipped problems) |
| `evaluation.run()` → `check_cache()` | `benchmark/evaluation.py:120` | `task` (cached `SolverTask`), cached `result` |
| `task/launcher.launch()` | `task/launcher.py:68` | `tids[tid]` (`SolverTask`), `result` from worker |

---

### `done()`

| Caller | File | Context |
|---|---|---|
| `task/launcher.launch()` | `task/launcher.py:83` | `finally` block after pool completes or raises |

---

### `status(new, n)`

| Caller | File | Args |
|---|---|---|
| `LogTalker.finished()` | `report/talker/logtalker.py:169` | `task.status(result)` → `True`/`False`/`None` |

---

## Tuning lifecycle

### `tuning(t_start, total)`

| Caller | File | Args |
|---|---|---|
| `tuner()` | `builder/autotune/autotune.py:66` | `time.time()`, `_total` (= `n_phases * iters_per_phase + (1 if init_params else 0)`) |

---

### `tuned(t_end)`

| Caller | File | Args |
|---|---|---|
| `tuner()` | `builder/autotune/autotune.py:129` | `time.time()` |

---

### `trials(nick, iters, timeout)`

| Caller | File | Args |
|---|---|---|
| `tune.tune()` | `builder/autotune/tune.py:28` | `nick` (phase name e.g. `"leaves"`), `iters` (per-phase count), `timeout` (per-phase seconds or `None`) |

---

### `trying(nick, it, values)`

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

### `tried(stats)`

| Caller | File | Args |
|---|---|---|
| `check.check()` | `builder/autotune/check.py:35` | `stats` dict with keys: `score`, `mlscore`, `valid_acc` (3-tuple), `train_acc` (3-tuple), `duration` |

---

### `trialed(nick)`

| Caller | File | Args |
|---|---|---|
| `tune.tune()` | `builder/autotune/tune.py:39` | `nick` (phase name, same as passed to `trials()`) |

---

### `building(f_mod, total)`

| Caller | File | Args |
|---|---|---|
| `build.model()` → `build_model()` via `report()` | `builder/autotune/build.py:82` | `f_mod` (path to model file), `params["num_round"]` (total LightGBM iterations) |

---

### `iteration(n, total, loss)`

| Caller | File | Args |
|---|---|---|
| `build.model()` → `iteration_callback()` via `report()` | `builder/autotune/build.py:59` | `env.iteration` (current step), `env.end_iteration` (total steps), `[r[2] for r in env.evaluation_result_list]` (loss values) |

---

### `built(score)`

| Caller | File | Args |
|---|---|---|
| `build.model()` → `check_model()` via `report()` | `builder/autotune/build.py:110` | `mlscore` = `POS_ACC_WEIGHT * acc[1] + acc[2]` |

---

### `result(val)`

| Caller | File | Args |
|---|---|---|
| `tuner()` | `builder/autotune/autotune.py:132` | `ret` = `(score, acc, trainacc, f_mod, duration, params, pos, neg)` |

---

## Logging helpers

### `info(msg)` / `debug(msg)`

| Caller | File | Args |
|---|---|---|
| `build.model()` via `report()` | `builder/autotune/build.py:57,74,92` | Debug strings (results list, early-stopping config, best iteration) |

These are only queued through `REMOTES` in the child process; in the parent they resolve to `logger.info` / no-op respectively.
