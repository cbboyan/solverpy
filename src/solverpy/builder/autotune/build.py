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

   def callback(env):
      results = env.evaluation_result_list
      loss = [r[2] for r in results]
      queue.put(("iteration", (env.iteration, env.end_iteration, loss)))

   d_mod = os.path.dirname(f_mod)
   os.makedirs(d_mod, exist_ok=True)
   f_log = f_mod + ".log"
   if queue: queue.put(("building", (f_mod, params["num_round"])))
   
   # build the model
   begin = time.time()
   callbacks = [lgb.log_evaluation(1), lgb.early_stopping(10, verbose=True)] 
   if queue: callbacks.append(callback)
   bst = lgb.train(
      params,
      dtrain, 
      #valid_sets=[dtrain, dtest],
      valid_sets=[dtest],
      callbacks=callbacks
   )
   end = time.time()
   bst.save_model(f_mod)

   # compute the accuracy on the testing data
   #(xs0, ys0) = testd
   acc = accuracy(bst, dtest.get_data(), dtest.get_label())
   trainacc = accuracy(bst, dtrain.get_data(), dtrain.get_label())
   bst.free_dataset()
   bst.free_network()

   # compute the score of this model
   score = POS_ACC_WEIGHT*acc[1] + acc[2]
   if queue: queue.put(("built", score))
   return (score, acc, trainacc, end-begin)
   
