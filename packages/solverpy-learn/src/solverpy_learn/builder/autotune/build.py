from typing import Any, TYPE_CHECKING
import os
import time
import lightgbm as lgb
import numpy as np

from solverpy.setups.evalset import Evalset
from solverpy.benchmark import evaluation
from solverpy.report.talker.talker import Talker

if TYPE_CHECKING:
   from lightgbm import Booster, Dataset
   from ..autotuner import AutoTuner

POS_ACC_WEIGHT = 2.0
ACCURACY_METRICS = (
   "accuracy",
   "positive_accuracy",
   "negative_accuracy",
)


def accuracy(
   preds: np.ndarray,
   data: "Dataset",
) -> list[tuple[str, float, bool]]:
   labels = data.get_label()
   assert isinstance(labels, np.ndarray)
   correct = (preds > 0.5) == labels

   def mean(mask: np.ndarray | None = None) -> float:
      selected = correct if mask is None else correct[mask]
      return float(selected.mean()) if selected.size else 0.0

   return [
      ("accuracy", mean(), True),
      ("positive_accuracy", mean(labels == 1), True),
      ("negative_accuracy", mean(labels == 0), True),
   ]


def metrics(
   results: list[tuple[Any, ...]] | None, ) -> dict[str, dict[str, float]]:
   values: dict[str, dict[str, float]] = {}
   for result in results or []:
      (dataset, metric, value) = result[:3]
      values.setdefault(dataset, {})[metric] = float(value)
   return values


def selected_metrics(
   bst: "Booster",
   same_data: bool,
) -> tuple[int, dict[str, dict[str, float]]]:
   current = bst.current_iteration()
   selected = bst.best_iteration if bst.best_iteration > 0 else current
   while bst.current_iteration() > selected:
      bst.rollback_one_iter()

   values = metrics(bst.eval_train(feval=accuracy))
   if same_data:
      values["valid"] = dict(values["train"])
   else:
      values.update(metrics(bst.eval_valid(feval=accuracy)))

   selected_values = {
      dataset: {
         metric: dataset_values[metric]
         for metric in ACCURACY_METRICS
      }
      for (dataset, dataset_values) in values.items()
   }
   return (selected, selected_values)


def accuracy_tuple(values: dict[str, float]) -> tuple[float, float, float]:
   return (
      values["accuracy"],
      values["positive_accuracy"],
      values["negative_accuracy"],
   )


def model(
      params: dict[str, Any],
      dtrain: "Dataset",
      dtest: "Dataset",
      f_mod: str,
      talker: Talker = Talker(),
) -> tuple["Booster", dict[str, Any]]:
   callbacks = bst = begin = end = mlscore = acc = trainacc = None
   same_data = dtrain is dtest

   def report(key: str, *content: Any) -> None:
      getattr(talker, key)(*content)

   def iteration_callback(env: Any) -> None:
      results = env.evaluation_result_list
      report("debug", str(results))
      report(
         "build_step",
         env.iteration + 1,
         env.end_iteration,
         metrics(results),
      )

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
         if rounds and same_data:
            report(
               "debug",
               "ignoring early stopping because training and validation data are identical",
            )
         elif rounds:
            report("debug",
                   f"activating early stopping: stopping_rounds={rounds}")
            callbacks.append(
               lgb.early_stopping(rounds, first_metric_only=True,
                                  verbose=True))
      callbacks.append(iteration_callback)

   def build_model() -> "Booster":
      nonlocal bst, begin, end, params, callbacks
      report("build_begin", f_mod, params["num_round"])
      begin = time.time()
      valid_sets = [dtrain] if same_data else [dtrain, dtest]
      valid_names = ["train"] if same_data else ["train", "valid"]
      bst = lgb.train(params,
                      dtrain,
                      valid_sets=valid_sets,
                      valid_names=valid_names,
                      keep_training_booster=True,
                      callbacks=callbacks)
      end = time.time()
      if hasattr(bst, "best_iteration"):
         report("debug",
                f"early stopping: best_iteration={bst.best_iteration}")
      return bst

   def check_model() -> None:
      nonlocal mlscore, acc, trainacc
      assert bst
      (selected, values) = selected_metrics(bst, same_data)
      report("build_selected", selected, values)
      trainacc = accuracy_tuple(values["train"])
      acc = accuracy_tuple(values["valid"])
      bst.save_model(f_mod)
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
   setup = builder._setup
   trains = setup["trains"]
   devels = setup["devels"] if "devels" in setup else trains
   assert "refs" in trains
   solver = devels.get("solver", setup.get("solver"))
   assert solver is not None
   modelname = f"{builder._dataname}/opt/{nick}"
   strategies = builder.applies(trains["refs"], modelname)
   evalset = Evalset(devels, strategies=strategies)
   evalset.pop("solvedby", None)
   assert "plugin" in evalset
   solver.call("trains", "disable")
   solver.call("debug-trains", "disable")
   talker.tune_eval_begin()
   res = evaluation.launch(evalset, **dict(setup, pool_context="spawn", talker=talker))
   talker.tune_eval_end(res)
   solved = lambda s, rs: sum(1 for r in rs.values() if s.solved(r))
   score = sum(solved(s, rs) for ((s, _, _), rs) in res.items())
   stats["score"] = score
   solver.call("trains", "enable")
   solver.call("debug-trains", "enable")
