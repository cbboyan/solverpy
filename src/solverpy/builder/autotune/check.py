import os
import logging

from ...tools import human
from . import build

logger = logging.getLogger(__name__)

def check(trial, params, dtrain, testd, d_tmp, usebar, **args):
   f_mod = os.path.join(d_tmp, "model%04d" % trial.number, "model.lgb")
   #barmsg = ("[trial %d]" % trial.number) if usebar else None
   (score, acc, dur) = build.model(params, dtrain, testd, f_mod)
   trial.set_user_attr(key="model", value=f_mod)
   trial.set_user_attr(key="score", value=score)
   trial.set_user_attr(key="acc", value=acc)
   trial.set_user_attr(key="time", value=dur)
   return score

def leaves(trial, params, min_leaves, max_leaves, **args):
   #num_leaves_base = trial.suggest_int('num_leaves_base', 16, 31)
   #num_leaves = round(2**(num_leaves_base/2))
   num_leaves = trial.suggest_int('num_leaves', min_leaves, max_leaves)
   params = dict(params, num_leaves=num_leaves)
   score = check(trial, params, **args)
   acc = human.humanacc(trial.user_attrs["acc"])
   logger.debug("- leaves trial %d: %s [num_leaves=%s]" % (trial.number, acc, params["num_leaves"]))
   return score

def bagging(trial, params, **args):
   bagging_freq = trial.suggest_int("bagging_freq", 1, 7)
   bagging_fraction = min(trial.suggest_float("bagging_fraction", 0.4, 1.0+1e-12), 1.0)
   params = dict(params, bagging_freq=bagging_freq, bagging_fraction=bagging_fraction)
   score = check(trial, params, **args)
   acc = human.humanacc(trial.user_attrs["acc"])
   logger.debug("- bagging trial %d: %s [freq=%s, frac=%s]" % (trial.number, acc, params["bagging_freq"], params["bagging_fraction"]))
   return score

def min_data(trial, params, **args):
   min_data = trial.suggest_int("min_data", 5, 10000)
   params = dict(params, min_data=min_data)
   score = check(trial, params, **args)
   acc = human.humanacc(trial.user_attrs["acc"])
   logger.debug("- min_data trial %d: %s [min_data=%s]" % (trial.number, acc, params["min_data"]))
   return score

def regular(trial, params, **args):
   lambda_l1 = trial.suggest_float("lambda_l1", 1e-8, 10.0)
   lambda_l2 = trial.suggest_float("lambda_l2", 1e-8, 10.0)
   params = dict(params, lambda_l1=lambda_l1, lambda_l2=lambda_l2)
   score = check(trial, params, **args)
   acc = human.humanacc(trial.user_attrs["acc"])
   logger.debug("- regular trial %d: %s [l1=%s, l2=%s]" % (trial.number, acc, params["lambda_l1"], params["lambda_l2"]))
   return score

