import os

from ...tools import human
from . import build

def check(trial, params, dtrain, dtest, d_tmp, queue, **args):
   f_mod = os.path.join(d_tmp, "model%04d" % trial.number, "model.lgb")
   (score, acc, trainacc, dur) = build.model(params, dtrain, dtest, f_mod, queue)
   trial.set_user_attr(key="model", value=f_mod)
   trial.set_user_attr(key="score", value=score)
   trial.set_user_attr(key="acc", value=acc)
   trial.set_user_attr(key="trainacc", value=trainacc)
   trial.set_user_attr(key="time", value=dur)
   if queue: queue.put(("tried", (score, acc, trainacc, dur)))
   return score

def leaves(trial, params, min_leaves, max_leaves, queue, **args):
   args = dict(args, queue=queue)
   #num_leaves_base = trial.suggest_int('num_leaves_base', 16, 31)
   #num_leaves = round(2**(num_leaves_base/2))
   num_leaves = trial.suggest_int('num_leaves', min_leaves, max_leaves)
   if queue: queue.put(("trying", ("leaves", trial.number, (num_leaves,))))
   params = dict(params, num_leaves=num_leaves)
   score = check(trial, params, **args)
   acc = human.humanacc(trial.user_attrs["acc"])
   return score

def bagging(trial, params, queue, **args):
   bagging_freq = trial.suggest_int("bagging_freq", 1, 7)
   bagging_fraction = min(trial.suggest_float("bagging_fraction", 0.4, 1.0+1e-12), 1.0)
   if queue: queue.put(("trying", ("bagging", trial.number, (bagging_freq, bagging_fraction))))
   params = dict(params, bagging_freq=bagging_freq, bagging_fraction=bagging_fraction)
   score = check(trial, params, queue=queue, **args)
   acc = human.humanacc(trial.user_attrs["acc"])
   return score

def min_data(trial, params, queue, **args):
   min_data = trial.suggest_int("min_data", 5, 10000)
   if queue: queue.put(("trying", ("min_data", trial.number, (min_data,))))
   params = dict(params, min_data=min_data)
   score = check(trial, params, queue=queue, **args)
   acc = human.humanacc(trial.user_attrs["acc"])
   return score

def regular(trial, params, queue, **args):
   lambda_l1 = trial.suggest_float("lambda_l1", 1e-8, 10.0)
   lambda_l2 = trial.suggest_float("lambda_l2", 1e-8, 10.0)
   if queue: queue.put(("trying", ("regular", trial.number, (lambda_l1, lambda_l2))))
   params = dict(params, lambda_l1=lambda_l1, lambda_l2=lambda_l2)
   score = check(trial, params, queue=queue, **args)
   acc = human.humanacc(trial.user_attrs["acc"])
   return score

