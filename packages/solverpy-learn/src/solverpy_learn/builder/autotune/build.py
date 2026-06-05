from typing import Any, TYPE_CHECKING
import os
import time
import lightgbm as lgb
from numpy import ndarray
from scipy.sparse import csr_matrix

from solverpy.setups import Setup
from solverpy.benchmark import evaluation
from solverpy.report.talker.talker import Talker

if TYPE_CHECKING:
   from lightgbm import Booster, Dataset
   from ..autotuner import AutoTuner

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
   talker: Talker = Talker(),
) -> tuple["Booster", dict[str, Any]]:
   callbacks = bst = begin = end = mlscore = acc = trainacc = None

   def report(key: str, *content: Any) -> None:
      getattr(talker, key)(*content)

   def iteration_callback(env: Any) -> None:
      results = env.evaluation_result_list
      report("debug", str(results))
      loss = [r[2] for r in results]
      report("build_step", env.iteration, env.end_iteration, loss)

   def setup_dirs() -> None:
      d_mod = os.path.dirname(f_mod)
      os.makedirs(d_mod, exist_ok=True)

   def setup_callbacks() -> None:
      nonlocal callbacks, params
      callbacks = []
      callbacks.append(lgb.log_evaluation(1))
      if "early_stopping" in params:
         params = dict(params)
         rounds = params.pop("early_stopping")
         rounds = 10 if (rounds is True) else int(rounds)
         if rounds:
            report("debug", f"activating early stopping: stopping_rounds={rounds}")
            callbacks.append(
               lgb.early_stopping(rounds, first_metric_only=True, verbose=True))
      callbacks.append(iteration_callback)

   def build_model() -> "Booster":
      nonlocal bst, begin, end, params, callbacks
      report("build_begin", f_mod, params["num_round"])
      begin = time.time()
      bst = lgb.train(
         params,
         dtrain,
         valid_sets=[dtrain, dtest],
         valid_names=["train", "valid"],
         callbacks=callbacks)
      end = time.time()
      if hasattr(bst, "best_iteration"):
         report("debug", f"early stopping: best_iteration={bst.best_iteration}")
      bst.save_model(f_mod)
      return bst

   def check_model() -> None:
      nonlocal mlscore, acc, trainacc
      assert bst
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
      mlscore = POS_ACC_WEIGHT * acc[1] + acc[2]
      report("build_done", mlscore)

   setup_dirs()
   setup_callbacks()
   bst = build_model()
   check_model()

   assert begin and end
   stats = dict(
      mlscore=mlscore,
      valid_acc=acc,
      train_acc=trainacc,
      duration=end - begin,
   )

   return (bst, stats)


def score(
   stats: dict[str, Any],
   builder: "AutoTuner | None",
   nick: str,
   talker: Talker = Talker(),
) -> None:
   if not builder:
      stats["score"] = stats["mlscore"]
      return
   assert "refs" in builder._trains
   modelname = f"{builder._dataname}/opt/{nick}"
   strategies = builder.applies(builder._trains["refs"], modelname)
   setup = Setup(builder._devels, strategies=strategies)
   setup["pool_context"] = "spawn"
   assert "solver" in setup
   assert "trains" in setup
   setup["solver"].call("trains", "disable")
   setup["solver"].call("debug-trains", "disable")
   talker.tune_eval_begin()
   res = evaluation.launch(talker=talker, **setup)
   talker.tune_eval_end(res)
   solved = lambda s, rs: sum(1 for r in rs.values() if s.solved(r))
   score = sum(solved(s, rs) for ((s, _, _), rs) in res.items())
   stats["score"] = score
   setup["solver"].call("trains", "enable")
   setup["solver"].call("debug-trains", "enable")
