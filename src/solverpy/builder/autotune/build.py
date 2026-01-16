from typing import Any, TYPE_CHECKING
import os
import time
import lightgbm as lgb
from numpy import ndarray
from scipy.sparse import csr_matrix

from ...setups import Setup
from ...benchmark import evaluation

if TYPE_CHECKING:
   from queue import Queue
   from lightgbm import Booster, Dataset
   from ..autotuner import AutoTuner
   Talker = Queue[tuple[str, tuple[Any, ...]]]

POS_ACC_WEIGHT = 2.0


def accuracy(
   bst: "Booster",
   xs: "csr_matrix",
   ys: "ndarray",
) -> tuple[float, float, float]:

   def getacc(pairs: list[tuple[float, float]]) -> float:
      if not pairs: return 0
      return sum([1 for (x, y) in pairs if int(x > 0.5) == y]) / len(pairs)

   if hasattr(bst, "best_iteration"):
      preds = bst.predict(xs, num_iteration=bst.best_iteration)
   else:
      preds = bst.predict(xs)

   assert type(preds) is ndarray
   preds0 = list(zip(preds, ys))
   acc = getacc(preds0)
   posacc = getacc([(x, y) for (x, y) in preds0 if y == 1])
   negacc = getacc([(x, y) for (x, y) in preds0 if y == 0])
   return (acc, posacc, negacc)


def model(
   params: dict[str, Any],
   dtrain: "Dataset",
   dtest: "Dataset",
   f_mod: str,
   queue: "Talker | None" = None,
) -> tuple["Booster", dict[str, Any]]:
   callbacks = bst = begin = end = mlscore = acc = trainacc = None

   def report(key: str, *content: Any) -> None:
      if queue:
         queue.put((key, content))

   def queue_callback(env: Any) -> None:
      results = env.evaluation_result_list
      report("debug", str(results))
      loss = [r[2] for r in results]
      report("iteration", env.iteration, env.end_iteration, loss)

   def setup_dirs() -> None:
      d_mod = os.path.dirname(f_mod)
      os.makedirs(d_mod, exist_ok=True)
      # f_log = f_mod + ".log"

   def setup_callbacks() -> None:
      nonlocal callbacks, params
      callbacks = []
      callbacks.append(lgb.log_evaluation(1))
      if "early_stopping" in params:
         # rounds = params["early_stopping"]
         params = dict(params)
         rounds = params.pop("early_stopping")  # this also removes it
         # rounds can be `bool` or `int` (or int-convertable)
         rounds = 10 if (rounds is True) else int(
            rounds)  # True => 10; False => 0
         if rounds:
            report("debug",
                   f"activating early stopping: stopping_rounds={rounds}")
            callbacks.append(
               lgb.early_stopping(rounds, first_metric_only=True,
                                  verbose=True))
      if queue:
         callbacks.append(queue_callback)

   def build_model() -> "Booster":
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
         callbacks=callbacks)
      end = time.time()
      if hasattr(bst, "best_iteration"):
         report("debug",
                f"early stopping: best_iteration={bst.best_iteration}")
      bst.save_model(f_mod)
      return bst

   def check_model() -> None:
      nonlocal mlscore, acc, trainacc
      assert bst
      # compute the accuracy on the testing data
      (axs, ays) = (dtest.get_data(), dtest.get_label())
      assert type(axs) is csr_matrix
      assert type(ays) is ndarray
      acc = accuracy(bst, axs, ays)
      (taxs, tays) = (dtrain.get_data(), dtrain.get_label())
      assert type(taxs) is csr_matrix
      assert type(tays) is ndarray
      trainacc = accuracy(bst, taxs, tays)
      bst.free_dataset()
      bst.free_network()
      # compute the mlscore of this model
      mlscore = POS_ACC_WEIGHT * acc[1] + acc[2]
      report("built", mlscore)

   setup_dirs()
   setup_callbacks()
   bst = build_model()  # make typing happy
   check_model()

   assert begin and end
   stats = dict(
      mlscore=mlscore,
      valid_acc=acc,
      train_acc=trainacc,
      duration=end - begin,
   )

   #return (mlscore, acc, trainacc, end-begin)
   return (bst, stats)


def score(
   stats: dict[str, Any],
   builder: "AutoTuner | None",
   nick: str,
) -> None:
   if not builder:
      stats["score"] = stats["mlscore"]
      return
   assert "refs" in builder._trains
   modelname = f"{builder._dataname}/opt/{nick}"
   sidlist = builder.applies(builder._trains["refs"], modelname)
   setup = Setup(builder._devels, sidlist=sidlist)
   assert "solver" in setup
   assert "trains" in setup
   setup["solver"].call("trains", "disable")
   setup["solver"].call("debug-trains", "disable")
   res = evaluation.launch(talker=builder.talker, **setup)
   solved = lambda s, rs: sum(1 for r in rs.values() if s.solved(r)) 
   score = sum(solved(s, rs) for ((s,_,_), rs) in res.items())
   stats["score"] = score
   setup["solver"].call("trains", "enable")
   setup["solver"].call("debug-trains", "enable")
