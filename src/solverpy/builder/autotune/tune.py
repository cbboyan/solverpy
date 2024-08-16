import os
import math
import optuna

from . import check

def tune(check_fun, nick, iters, timeout, d_tmp, queue=None, sampler=None, **args):
   d_tmp = os.path.join(d_tmp, nick)
   if queue: queue.put(("TRIALS", (nick, iters, timeout)))
   study = optuna.create_study(direction='maximize', sampler=sampler)
   objective = lambda trial: check_fun(trial, d_tmp=d_tmp, queue=queue, **args)
   study.optimize(objective, n_trials=iters, timeout=timeout)
   best = tuple(study.best_trial.user_attrs[x] for x in ["score", "acc", "model", "time"])
   return (best, study.best_trial.params)

def leaves_grid(min_leaves, max_leaves, **args):
   args = dict(args, min_leaves=min_leaves, max_leaves=max_leaves)
   min_base = round(2*math.log2(min_leaves))
   max_base = round(2*math.log2(max_leaves))
   values = list([round(2**(n/2)) for n in range(min_base, max_base+1)])
   sampler = optuna.samplers.GridSampler({"num_leaves": values})
   return tune(check.leaves, "leaves", sampler=sampler, **args)

def bagging(**args):
   return tune(check.bagging, "bagging", **args)

def min_data(**args):
   values = [5, 10, 20, 50, 100, 500, 1000, 2000, 5000, 10000]
   sampler = optuna.samplers.GridSampler({"min_data": values})
   return tune(check.min_data, "min_data", sampler=sampler, **args)

def regular(**args):
   return tune(check.regular, "regular", **args)

