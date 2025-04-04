#!/usr/bin/env python3

import os
import time
import logging
import lightgbm as lgb

from ...tools import human
from ...builder import svm
from . import tune

POS_ACC_WEIGHT = 2.0

def accuracy(bst, xs, ys):

   def getacc(pairs):
      if not pairs: return 0
      return sum([1 for (x,y) in pairs if int(x>0.5)==y]) / len(pairs)

   if hasattr(bst, "best_iteration"):
      preds = bst.predict(xs, num_iteration=bst.best_iteration)
   else:
      preds = bst.predict(xs)
      
   preds = list(zip(preds, ys))
   acc = getacc(preds)
   posacc = getacc([(x,y) for (x,y) in preds if y==1])
   negacc = getacc([(x,y) for (x,y) in preds if y==0])
   return (acc, posacc, negacc)

def model(params, dtrain, dtest, f_mod, queue):
   callbacks = bst = begin = end = score = acc = trainacc = None
   
   def report(key, *content):
      if queue:
         queue.put((key,content))

   def queue_callback(env):
      results = env.evaluation_result_list
      loss = [r[2] for r in results]
      report("iteration", env.iteration, env.end_iteration, loss)

   def setup_dirs():
      d_mod = os.path.dirname(f_mod)
      os.makedirs(d_mod, exist_ok=True)
      # f_log = f_mod + ".log"

   def setup_callbacks():
      nonlocal callbacks, params
      callbacks = []
      callbacks.append(lgb.log_evaluation(1))
      if "early_stopping" in params:
         # rounds = params["early_stopping"] 
         params = dict(params)
         rounds = params.pop("early_stopping") # this also removes it
         # rounds can be `bool` or `int` (or int-convertable)
         rounds = 10 if (rounds is True) else int(rounds) # True => 10; False => 0
         if rounds:
            report("debug", f"activating early stopping: stopping_rounds={rounds}")
            callbacks.append(lgb.early_stopping(rounds, verbose=True))
      if queue: 
         callbacks.append(queue_callback)
   
   def build_model():
      nonlocal bst, begin, end, params, callbacks
      # build the model
      report("building", f_mod, params["num_round"])
      begin = time.time()
      bst = lgb.train(
         params,
         dtrain, 
         valid_sets=[dtrain, dtest],
         valid_names=["train", "valid"],
         # valid_sets=[dtest],
         callbacks=callbacks
      )
      end = time.time()
      if hasattr(bst, "best_iteration"):
         report("debug", f"early stopping: best_iteration={bst.best_iteration}")
      bst.save_model(f_mod)

   def check_model():
      nonlocal score, acc, trainacc
      # compute the accuracy on the testing data
      # (xs0, ys0) = testd
      acc = accuracy(bst, dtest.get_data(), dtest.get_label())
      trainacc = accuracy(bst, dtrain.get_data(), dtrain.get_label())
      bst.free_dataset()
      bst.free_network()
      # compute the score of this model
      score = POS_ACC_WEIGHT*acc[1] + acc[2]
      report("built", score)

   setup_dirs()
   setup_callbacks()
   build_model()
   check_model()

   stats = dict(
      score=score,
      valid_acc=acc,
      train_acc=trainacc,
      duration=end-begin,
   )
   
   #return (score, acc, trainacc, end-begin)
   return (bst, stats)
   
