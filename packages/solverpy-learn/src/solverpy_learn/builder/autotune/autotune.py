from typing import Any, Callable, TYPE_CHECKING
import os
import time
import lightgbm as lgb
import multiprocessing

from solverpy.tools import human, redirect
from solverpy.report.talker.talker import Talker
from solverpy.report.talker.remotetalker import RemoteTalker
from .. import svm
from . import tune, build

if TYPE_CHECKING:
   from .tune import TuneResult
   from ..autotuner import AutoTuner

PHASES: dict[str, Callable[..., "TuneResult"]] = {
   "l": tune.leaves_grid,
   "b": tune.bagging,
   "r": tune.regular,
   "m": tune.min_data,
   "d": tune.depth,
   "e": tune.learning_rate,
   "w": tune.posneg_weight,
}

DEFAULTS: dict[str, Any] = {
   'learning_rate': 0.15,
   'objective': 'binary',
   'num_round': 200,
   'max_depth': 0,
   'num_leaves': 300,
   # default values from the docs:
   'min_data': 20,
   'max_bin': 255,
   'feature_fraction': 1.0,
   'bagging_fraction': 1.0,
   'bagging_freq': 0,
   'lambda_l1': 0.0,
   'lambda_l2': 0.0,
}


def tuner(
   f_train: str,
   f_test: str,
   d_tmp: str = "optuna-tmp",
   phases: str = "l:b:m:r",
   iters: int = 100,
   timeout: (int | None) = None,
   init_params: (dict[str, Any] | None) = None,
   min_leaves: int = 16,
   max_leaves: int = 2048,
   talker: "Talker" = Talker(),
   atpeval: bool = False,
   posneg_weight: float = 0,
   builder: "AutoTuner | None" = None,
) -> tuple[Any, ...] | None:
   assert bool(atpeval) == bool(builder)
   Talker.log_config(talker._log_queue)

   _n_phases = len(phases.split(":"))
   _iters0 = (iters // _n_phases) if iters else 0
   _total = _n_phases * _iters0 + (1 if init_params is not None else 0)
   talker.tune_begin(time.time(), _total)
   (xs, ys) = svm.load(f_train)
   dtrain = lgb.Dataset(xs, label=ys, free_raw_data=False)
   dtrain.construct()
   (xs0, ys0) = svm.load(f_test) if f_test != f_train else (xs, ys)
   dtest = lgb.Dataset(xs0, label=ys0, free_raw_data=False)
   dtest.construct()

   os.makedirs(d_tmp, exist_ok=True)

   phases0 = phases.split(":")
   params = dict(DEFAULTS)
   if init_params: params.update(init_params)
   pos = sum(ys)
   neg = len(ys) - pos
   if "w" in phases0:
      params["scale_pos_weight"] = neg / pos
      talker.debug(f"posneg balancing: base scale_pos_weight = {params['scale_pos_weight']} (tuning multiplier)")
   elif posneg_weight == 0:
      params["is_unbalance"] = "true" if neg != pos else "false"
      talker.debug(f"posneg balancing: is_unbalance = {params['is_unbalance']}")
   else:
      params["scale_pos_weight"] = posneg_weight * (neg / pos)
      talker.debug(f"posneg balancing: scale_pos_weight = {params['scale_pos_weight']}")

   if "m" in phases:
      params["feature_pre_filter"] = "false"
   timeout0 = timeout / len(phases0) if timeout else None
   iters0 = iters // len(phases0) if iters else None
   args = dict(
      dtrain=dtrain,
      dtest=dtest,
      d_tmp=d_tmp,
      iters=iters0,
      timeout=timeout0,
      talker=talker,
      min_leaves=min_leaves,
      max_leaves=max_leaves,
      builder=builder,
   )

   if init_params is not None:
      f_mod = os.path.join(d_tmp, "init", "model.lgb")
      (_, stats) = build.model(params, dtrain, dtest, f_mod, talker)
      build.score(stats, builder, "init", talker)
      acc = stats["valid_acc"]
      best = (
         stats["score"],
         acc,
         stats["train_acc"],
         f_mod,
         stats["duration"],
      )
      talker.debug("- initial model: %s" % human.humanacc(acc))
   else:
      best = (-1, None, None, None, None)

   for phase in phases0:
      (best0, params0) = PHASES[phase](params=params, **args)
      if best0[0] > best[0]:
         best = best0
         params.update(params0)

   talker.tune_end(time.time())
   ret = best + (params, pos, neg)
   talker.tune_result(ret)
   return ret


def prettytuner(talker: Talker = Talker(), *args, **kwargs) -> Any:
   remote = RemoteTalker(talker, queue=multiprocessing.Queue())

   d_tmp = kwargs.get("d_tmp") or "tune-tmp"
   os.makedirs(d_tmp, exist_ok=True)
   ctx = multiprocessing.get_context("fork")
   kwargs["talker"] = remote
   kwargs["f_log"] = os.path.join(d_tmp, "autotune.log")
   kwargs["target"] = tuner
   p = ctx.Process(target=redirect.call, args=args, kwargs=kwargs)

   remote.listening_start()
   talker._log_queue = remote._log_queue  # propagate so eval_launch injects into ATP workers
   try:
      p.start()
      p.join()
   except BaseException:
      p.terminate()
      talker.terminate()
      raise
   finally:
      remote.listening_stop()
      talker._log_queue = None
   return talker._result
