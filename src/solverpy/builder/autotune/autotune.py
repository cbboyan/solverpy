#!/usr/bin/env python3

import os
import time
import logging
import lightgbm as lgb
import multiprocessing

from ...tools import human, redirect
from ...trains import svm
from ...task.bar import BuilderBar
from . import tune, build

logger = logging.getLogger(__name__)

PHASES = {
   "l": tune.leaves_grid,
   "b": tune.bagging,
   "r": tune.regular,
   "m": tune.min_data,
}

DEFAULTS = {
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
   f_train,
   f_test, 
   d_tmp="optuna-tmp", 
   phases="l:b:m:r", 
   iters=100, 
   timeout=None, 
   init_params=None, 
   min_leaves=16, 
   max_leaves=2048,
   queue=None,
):
   if queue: queue.put(("TUNING", time.time()))
   (xs, ys) = svm.load(f_train)
   dtrain = lgb.Dataset(xs, label=ys)
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
   phases = phases.split(":")
   if "m" in phases:
      params["feature_pre_filter"] = "false" 
   timeout = timeout / len(phases) if timeout else None
   iters = iters // len(phases) if iters else None
   args = dict(
      dtrain=dtrain, 
      dtest=dtest, 
      d_tmp=d_tmp, 
      iters=iters, 
      timeout=timeout, 
      queue=queue,
      min_leaves=min_leaves, 
      max_leaves=max_leaves,
   )

   if init_params is not None:
      f_mod = os.path.join(d_tmp, "init", "model.lgb")
      (score, acc, dur) = build.model(params, dtrain, dtest, f_mod, queue)
      best = (score, acc, f_mod, dur)
      logger.debug("- initial model: %s" % human.humanacc(acc)) 
   else:
      best = (-1, None, None, None)

   for phase in phases:
      (best0, params0) = PHASES[phase](params=params, **args)
      if best0[0] > best[0]:
         best = best0 
         params.update(params0)
   
   if queue: queue.put(("TUNED", time.time()))
   ret = best + (params, pos, neg)
   if queue: 
      queue.put(("RESULT", ret))
   else:
      return ret

def prettytuner(*args, **kwargs):
   
   bar = None
   desc = "trial"
   iters = ""
   t_start = 0
   t_end = 0

   def handle(msg):
      nonlocal bar, desc, iters, t_start, t_end
      (key, val) = msg
      if key == "RESULT":
         return val
      elif key == "BUILD":
         (f_mod, total) = val
         logger.debug(f"building model: {f_mod}")
         bar = BuilderBar(total, desc)
      elif key == "ITER":
         (n, total, loss) = val
         bar.done(loss)
      elif key == "BUILT":
         bar.close()
         logger.info(f"Trail score: {val:.4f}")
      elif key == "TRIALS":
         (nick, iters, timeout) = val
         iters = f"/{iters}" if iters else ""
      elif key == "TRY":
         (nick, it, values) = val
         desc = f"{nick}[{it+1}{iters}]"
         values = ", ".join("%.4f"%v if type(v) is float else str(v) for v in values)
         logger.info(f"Starting trial: {desc}: ({values})")
      elif key == "TRIED":
         logger.info(f"Trial accuracy: {human.humanacc(val)}")
      elif key == "TUNING":
         t_start = val
      elif key == "TUNED":
         t_end = val
      else:
         print(msg)
      return None

   queue = multiprocessing.Queue()
   kwargs["queue"] = queue
   kwargs["f_log"] = "autotune.log"
   kwargs["target"] = tuner
   p = multiprocessing.Process(target=redirect.call, args=args, kwargs=kwargs)

   try:
      p.start()
      while True:
         msg = queue.get()
         result = handle(msg)
         if result: 
            break
   except (Exception, KeyboardInterrupt) as e:
      p.terminate()
      raise e
   finally:
      p.join()

   return result

