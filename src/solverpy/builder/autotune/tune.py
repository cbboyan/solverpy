from typing import Any, Callable, TYPE_CHECKING
import os
import math
import optuna

from . import check

if TYPE_CHECKING:
   from .build import Talker
   from optuna.samplers import BaseSampler

#UserAttrs = tuple[Any, ...]
UserAttrs = tuple[float, float, float, str, float]
TuneResult = tuple[UserAttrs, dict[str, Any]]


def tune(
   check_fun: Callable[..., float],
   nick: str,
   iters: int,
   timeout: (int | None),
   d_tmp: str,
   queue: "Talker | None" = None,
   sampler: "BaseSampler | None" = None,
   **args: Any,
) -> TuneResult:
   d_tmp = os.path.join(d_tmp, nick)
   if queue: queue.put(("trials", (nick, iters, timeout)))
   study = optuna.create_study(direction='maximize', sampler=sampler)
   objective = lambda trial: check_fun(trial, d_tmp=d_tmp, queue=queue, nick=nick, **args)
   study.optimize(objective, n_trials=iters, timeout=timeout)
   best = tuple(study.best_trial.user_attrs[x] for x in [
      "score",
      "acc",
      "trainacc",
      "model",
      "time",
   ])
   if queue: queue.put(("trialed", (nick,)))
   return (best, study.best_trial.params)


def leaves_grid(min_leaves: int, max_leaves: int, **args: Any) -> TuneResult:
   args = dict(args, min_leaves=min_leaves, max_leaves=max_leaves)
   min_base = round(2 * math.log2(min_leaves))
   max_base = round(2 * math.log2(max_leaves))
   values = list([round(2**(n / 2)) for n in range(min_base, max_base + 1)])
   sampler = optuna.samplers.GridSampler({"num_leaves": values})
   return tune(check.leaves, "leaves", sampler=sampler, **args)


def bagging(**args: Any) -> TuneResult:
   return tune(check.bagging, "bagging", **args)


def min_data(**args: Any) -> TuneResult:
   values = [5, 10, 20, 50, 100, 500, 1000, 2000, 5000, 10000]
   sampler = optuna.samplers.GridSampler({"min_data": values})
   return tune(check.min_data, "min_data", sampler=sampler, **args)


def regular(**args: Any) -> TuneResult:
   return tune(check.regular, "regular", **args)


def depth(**args: Any) -> TuneResult:
   return tune(check.depth, "depth", **args)
