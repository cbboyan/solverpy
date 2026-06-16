import gc
import weakref
from types import SimpleNamespace

import lightgbm as lgb
import numpy as np
import pytest
from lightgbm.basic import LightGBMError
from scipy.sparse import csr_matrix

from solverpy.report.talker.talker import Talker
from solverpy_learn.builder.autotune import autotune, build


class RecordingTalker(Talker):

   def __init__(self):
      super().__init__()
      self.steps = []
      self.selected = []
      self.debugs = []

   def build_step(self, n, total, metrics):
      self.steps.append((n, total, metrics))

   def build_selected(self, iteration, metrics):
      self.selected.append((iteration, metrics))

   def debug(self, msg):
      self.debugs.append(msg)


def dataset(xs, ys, reference=None):
   data = lgb.Dataset(
      csr_matrix(np.array(xs, dtype=np.float64)),
      label=np.array(ys),
      reference=reference,
      params={
         "feature_pre_filter": False,
         "min_data": 1,
      },
      free_raw_data=True,
   )
   data.construct()
   return data


def test_accuracy_returns_vectorized_threshold_metrics():

   class Data:

      def get_label(self):
         return np.array([0, 0, 1, 1])

   values = build.accuracy(np.array([0.1, 0.9, 0.4, 0.8]), Data())

   assert values == [
      ("accuracy", 0.5, True),
      ("positive_accuracy", 0.5, True),
      ("negative_accuracy", 0.5, True),
   ]


def test_datasets_release_inputs_and_reuse_same_file(monkeypatch):
   references = []
   constructed = []
   dataset_references = []
   events = []

   class Dataset:

      def __init__(
         self,
         xs,
         label,
         params,
         free_raw_data,
         reference=None,
      ):
         assert free_raw_data is True
         assert params is None
         references.extend([weakref.ref(xs), weakref.ref(label)])
         constructed.append(self)
         dataset_references.append(reference)

      def construct(self):
         events.append("construct")
         return self

   def load(path):
      events.append(f"load:{path}")
      return (
         np.array([[0.0], [1.0]]),
         np.array([0, 1]),
      )

   monkeypatch.setattr(autotune.svm, "load", load)
   monkeypatch.setattr(autotune.lgb, "Dataset", Dataset)

   (dtrain, dtest, pos, neg) = autotune._datasets("same", "same")
   gc.collect()

   assert dtrain is dtest
   assert len(constructed) == 1
   assert dataset_references == [None]
   assert (pos, neg) == (1, 1)
   assert events == ["load:same", "construct"]
   assert all(reference() is None for reference in references)

   references.clear()
   constructed.clear()
   dataset_references.clear()
   events.clear()
   (dtrain, dtest, pos, neg) = autotune._datasets("train", "valid")
   gc.collect()

   assert dtrain is not dtest
   assert len(constructed) == 2
   assert dataset_references == [None, dtrain]
   assert (pos, neg) == (1, 1)
   assert events == ["load:train", "load:valid", "construct", "construct"]
   assert all(reference() is None for reference in references)


def test_model_reports_structured_and_selected_metrics(tmp_path):
   dtrain = dataset(
      [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]],
      [0, 0, 0, 1, 1, 1],
   )
   dvalid = dataset(
      [[0, 0], [0, 1], [1, 1], [2, 0]],
      [0, 0, 1, 1],
      reference=dtrain,
   )
   talker = RecordingTalker()
   params = dict(
      objective="binary",
      metric="binary_logloss",
      num_round=20,
      num_leaves=4,
      min_data=1,
      learning_rate=0.2,
      early_stopping=3,
      verbosity=-1,
   )

   (bst, stats) = build.model(
      params,
      dtrain,
      dvalid,
      str(tmp_path / "model.lgb"),
      talker,
   )

   assert talker.steps
   assert talker.steps[0][0] == 1
   assert set(talker.steps[0][2]) == {"train", "valid"}
   assert talker.selected == [(
      bst.current_iteration(),
      {
         "train": {
            "accuracy": stats["train_acc"][0],
            "positive_accuracy": stats["train_acc"][1],
            "negative_accuracy": stats["train_acc"][2],
         },
         "valid": {
            "accuracy": stats["valid_acc"][0],
            "positive_accuracy": stats["valid_acc"][1],
            "negative_accuracy": stats["valid_acc"][2],
         },
      },
   )]
   with pytest.raises(LightGBMError, match="freed raw data"):
      dtrain.get_data()
   with pytest.raises(LightGBMError, match="freed raw data"):
      dvalid.get_data()


def test_same_dataset_is_not_duplicated_or_used_for_early_stopping(
   monkeypatch,
   tmp_path,
):
   data = dataset(
      [[0, 0], [0, 1], [1, 0], [1, 1]],
      [0, 0, 1, 1],
   )
   talker = RecordingTalker()

   def early_stopping(*args, **kwargs):
      del args, kwargs
      raise AssertionError("early stopping must not be enabled")

   monkeypatch.setattr(build.lgb, "early_stopping", early_stopping)
   params = dict(
      objective="binary",
      metric="binary_logloss",
      num_round=3,
      num_leaves=2,
      min_data=1,
      early_stopping=2,
      verbosity=-1,
   )

   (_, stats) = build.model(
      params,
      data,
      data,
      str(tmp_path / "model.lgb"),
      talker,
   )

   assert stats["train_acc"] == stats["valid_acc"]
   assert all(set(metrics) == {"train"} for (_, _, metrics) in talker.steps)
   assert talker.selected[0][1]["train"] == talker.selected[0][1]["valid"]
   assert any("ignoring early stopping" in msg for msg in talker.debugs)


def test_score_does_not_restrict_tuning_evaluation_with_solvedby(monkeypatch):
   calls = []

   class Solver:

      def call(self, *args):
         calls.append(args)

   solver = Solver()
   builder = SimpleNamespace(
      _dataname="experiment",
      _setup={
         "evals": {
            "refs": ["reference"],
         },
         "devels": {
            "solver": solver,
            "plugin": object(),
            "benchmarks": ["development"],
            "strategies": ["reference"],
            "solvedby": "reference",
         },
         "it": 0,
      },
      applies=lambda refs, model: [f"{refs[0]}-{model}"],
   )
   launched_evalset = {}
   launched_setup = {}

   def launch(evalset, talker=None, **setup):
      launched_evalset.update(evalset)
      launched_setup.update(setup)
      return {}

   monkeypatch.setattr(build.evaluation, "launch", launch)
   stats = {}

   build.score(stats, builder, "trial")

   assert "solvedby" not in launched_evalset
   assert launched_evalset["pool_context"] == "spawn"
   assert "pool_context" not in launched_setup
   assert launched_setup["it"] == 0
   assert launched_evalset["benchmarks"] == ["development"]
   assert stats["score"] == 0
   assert calls == [
      ("trains", "disable"),
      ("debug-trains", "disable"),
      ("trains", "enable"),
      ("debug-trains", "enable"),
   ]
