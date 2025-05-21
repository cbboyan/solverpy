from typing import Any, Callable, TYPE_CHECKING
import os
import time
import logging
import lightgbm as lgb
import multiprocessing

from ...tools import human, redirect
from ...builder import svm
from . import tune, build
from .listener import AutotuneListener

if TYPE_CHECKING:
   from queue import Queue
   from .tune import TuneResult

logger = logging.getLogger(__name__)

PHASES: dict[str, Callable[..., "TuneResult"]] = {
   "l": tune.leaves_grid,
   "b": tune.bagging,
   "r": tune.regular,
   "m": tune.min_data,
   "d": tune.depth,
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
   queue: Queue[Any] | None = None,
) -> tuple[Any, ...] | None:
   if queue: queue.put(("tuning", time.time()))
   (xs, ys) = svm.load(f_train)
   dtrain = lgb.Dataset(xs, label=ys, free_raw_data=False)
   dtrain.construct()
   (xs0, ys0) = svm.load(f_test) if f_test != f_train else (xs, ys)
   dtest = lgb.Dataset(xs0, label=ys0, free_raw_data=False)
   dtest.construct()

   os.makedirs(d_tmp, exist_ok=True)

   params = dict(DEFAULTS)
   if init_params: params.update(init_params)
   pos = sum(ys)
   neg = len(ys) - pos
   #params["scale_pos_weight"] = neg / pos
   params["is_unbalance"] = "true" if neg != pos else "false"
   phases0 = phases.split(":")
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
      queue=queue,
      min_leaves=min_leaves,
      max_leaves=max_leaves,
   )

   if init_params is not None:
      f_mod = os.path.join(d_tmp, "init", "model.lgb")
      #(score, acc, trainacc, dur) = build.model(params, dtrain, dtest, f_mod, queue)
      (_, stats) = build.model(params, dtrain, dtest, f_mod, queue)
      acc = stats["valid_acc"]
      best = (stats["score"], acc, stats["train_acc"], f_mod,
              stats["duration"])
      logger.debug("- initial model: %s" % human.humanacc(acc))
   else:
      best = (-1, None, None, None, None)

   for phase in phases0:
      (best0, params0) = PHASES[phase](params=params, **args)
      if best0[0] > best[0]:
         best = best0
         params.update(params0)

   if queue: queue.put(("tuned", time.time()))
   ret = best + (params, pos, neg)
   if queue:
      queue.put(("result", (ret, )))
   else:
      return ret


def prettytuner(*args, **kwargs) -> Any:

   listener = AutotuneListener()

   d_tmp = kwargs["d_tmp"]
   os.makedirs(d_tmp, exist_ok=True)
   queue = multiprocessing.Queue()
   kwargs["queue"] = queue
   kwargs["f_log"] = os.path.join(d_tmp, "autotune.log")
   kwargs["target"] = tuner
   p = multiprocessing.Process(target=redirect.call, args=args, kwargs=kwargs)

   try:
      p.start()
      while True:
         msg = queue.get()
         result = listener.listen(msg)
         if result:
            break
   except (Exception, KeyboardInterrupt) as e:
      p.terminate()
      raise e
   finally:
      p.join()

   return result
