"""
ML learning loop tests for solverpy-learn.

Tests the full eprover training + enigma loop with both ATP-eval and ML-eval
configurations.  These tests run the iterative eval/build loop and verify that
the expected trains and models are produced in the database.

Run with:
   SOLVERPY_BENCHMARKS=tests/data/problems \
   SOLVERPY_DB=tests/data/solverpy_db \
   pytest -m learn tests/test_learn_loop.py
"""

import shutil
import pytest
from pathlib import Path

DATA_DIR   = Path(__file__).parent / "data"
DB_DIR     = DATA_DIR / "solverpy_db"
STRATS_DIR = DB_DIR / "strats"

LOOP_CASES = [
   pytest.param(
      dict(
         sid="eprover-mzr02@v=atpeval",
         train_dataname="eprover-atp/train",
         devel_dataname="eprover-atp/devel",
         tune=dict(
            phases="l:b:m:r",
            atpeval=True,
            timeout=None,
            iters=8,
            min_leaves=8,
            max_leaves=256,
            init_params=dict(
               metric=["auc", "binary", "binary_error"],
               num_round=50,
               num_leaves=4,
               early_stopping=10,
            ),
         ),
      ),
      id="eprover-atpeval",
      marks=pytest.mark.learn,
   ),
   pytest.param(
      dict(
         sid="eprover-mzr02@v=mleval",
         train_dataname="eprover-ml/train",
         devel_dataname="eprover-ml/devel",
         tune=dict(
            phases="l:b:m:r",
            timeout=None,
            iters=8,
            min_leaves=8,
            max_leaves=256,
            init_params=dict(
               metric="auc",
               num_round=50,
               num_leaves=4,
               early_stopping=10,
            ),
         ),
      ),
      id="eprover-mleval",
      marks=pytest.mark.learn,
   ),
]


@pytest.fixture(scope="module")
def learn_env():
   """Clean the learn DB (keep strats/), set env vars, and leave files for inspection."""
   import os
   import solverpy.benchmark.path.bids as bids_mod

   for d in DB_DIR.iterdir():
      if d.name != "strats" and d.is_dir():
         shutil.rmtree(d)

   os.environ["SOLVERPY_DB"] = str(DB_DIR)
   os.environ["SOLVERPY_BENCHMARKS"] = str(DATA_DIR / "problems")
   bids_mod.problems.__defaults__[0].clear()

   yield DB_DIR

   os.environ.pop("SOLVERPY_DB", None)
   os.environ.pop("SOLVERPY_BENCHMARKS", None)
   bids_mod.problems.__defaults__[0].clear()


@pytest.fixture(params=LOOP_CASES, scope="module")
def loop_result(request, learn_env):
   """Run the full eprover + enigma loop and return (db, case_params)."""
   from solverpy_learn import setups

   p = request.param
   sid = p["sid"]

   common = setups.Setup(
      limit="T1",
      options=["outputs", "debug-trains", "headless"],
      loops=2,
      cores=4,
      binary="eprover-ho",
      sel_features="C(l,x,s,r,v[b=2048],h,c,d,t,a):M:F:S:G",
      posneg_ratio=10,
      posneg_weight=2,
   )

   setup = setups.Setup(
      common,
      sidlist=[sid],
      bidlist=["isa/mesh20train"],
      dataname=p["train_dataname"],
      refs=[sid],
   )

   devel = setups.Setup(
      common,
      sidlist=[sid],
      bidlist=["isa/mesh10test"],
      dataname=p["devel_dataname"],
      refs=[sid],
   )

   setups.eprover(setup, training=True)
   setups.evaluation(setup)

   setups.eprover(devel, training=True)
   setups.evaluation(devel)

   setups.enigma(setup, devel, tunesel=p["tune"])
   setups.launch(setup, devel)

   return learn_env, p


# --- top-level DB directories ---

def test_trains_dir_exists(loop_result):
   db, _ = loop_result
   assert (db / "trains").is_dir()


def test_models_dir_exists(loop_result):
   db, _ = loop_result
   assert (db / "models").is_dir()


# --- loop directory counts ---

def test_train_has_two_loops(loop_result):
   db, p = loop_result
   train_base = db / "trains" / p["train_dataname"]
   loops = sorted(d.name for d in train_base.iterdir() if d.is_dir() and d.name.startswith("loop"))
   assert loops == ["loop00", "loop01"], f"Expected loop00+loop01 in train, got {loops}"


def test_devel_has_three_loops(loop_result):
   db, p = loop_result
   devel_base = db / "trains" / p["devel_dataname"]
   loops = sorted(d.name for d in devel_base.iterdir() if d.is_dir() and d.name.startswith("loop"))
   assert loops == ["loop00", "loop01", "loop02"], f"Expected loop00-loop02 in devel, got {loops}"


# --- loop00 contents (train and devel) ---

def _sel_dir(base: Path, loop: str) -> Path:
   """Return the sel_... subdirectory inside a loop dir."""
   loop_dir = base / loop
   sel_dirs = [d for d in loop_dir.iterdir() if d.is_dir() and d.name.startswith("sel_")]
   assert len(sel_dirs) == 1, f"Expected one sel_... dir in {loop_dir}, got {sel_dirs}"
   return sel_dirs[0]


def test_train_loop00_files(loop_result):
   db, p = loop_result
   sel = _sel_dir(db / "trains" / p["train_dataname"], "loop00")
   for fname in ["train.in-data.npz", "train.in-label.npz", "train.in-stats.txt"]:
      assert (sel / fname).exists(), f"Missing {fname} in {sel}"


def test_devel_loop00_files(loop_result):
   db, p = loop_result
   sel = _sel_dir(db / "trains" / p["devel_dataname"], "loop00")
   for fname in ["train.in-data.npz", "train.in-label.npz", "train.in-stats.txt"]:
      assert (sel / fname).exists(), f"Missing {fname} in {sel}"


# --- loop01+ contents (addon + merged train) ---

def test_train_loop01_files(loop_result):
   db, p = loop_result
   sel = _sel_dir(db / "trains" / p["train_dataname"], "loop01")
   for fname in [
      "addon.in-data.npz", "addon.in-label.npz", "addon.in-stats.txt",
      "train.in-data.npz", "train.in-label.npz",
   ]:
      assert (sel / fname).exists(), f"Missing {fname} in {sel}"


def test_devel_loop01_files(loop_result):
   db, p = loop_result
   sel = _sel_dir(db / "trains" / p["devel_dataname"], "loop01")
   for fname in [
      "addon.in-data.npz", "addon.in-label.npz", "addon.in-stats.txt",
      "train.in-data.npz", "train.in-label.npz",
   ]:
      assert (sel / fname).exists(), f"Missing {fname} in {sel}"


# --- model files ---

def test_model_enigma_map_exists(loop_result):
   db, _ = loop_result
   maps = list((db / "models").rglob("enigma.map"))
   assert len(maps) > 0, "No enigma.map found under models/"


def test_model_lgb_exists(loop_result):
   db, _ = loop_result
   lgbs = list((db / "models").rglob("model.lgb"))
   assert len(lgbs) > 0, "No model.lgb found under models/"
