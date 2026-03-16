"""
Tests for benchmark evaluation using the solverpy evaluation pipeline.
Results are cached in tests/data/solverpy_db/ and reused across test runs.
"""

import shutil
import pytest
from pathlib import Path

from solverpy import setups
from solverpy.benchmark.db.providers.jsons import JsonsStore
from solverpy.benchmark.db.providers.solved import Solved
from solverpy.benchmark.db.providers.status import Status
from solverpy.benchmark.path import bids, sids

DATA_DIR = Path(__file__).parent / "data"
DB_DIR   = DATA_DIR / "solverpy_db"

# (solver_setup_fn, bidlist, sidlist)
EVAL_CASES = [
   pytest.param(
      (setups.eprover, ["problems/bushy010"], ["eprover-default"]),
      id="eprover-bushy010-default",
   ),
   pytest.param(
      (setups.vampire, ["problems/bushy010"], ["vampire-default"]),
      id="vampire-bushy010-default",
   ),
   pytest.param(
      (setups.cvc5, ["problems/smt010"], ["cvc5-enum"]),
      id="cvc5-smt010-enum",
   ),
]


@pytest.fixture(scope="module")
def solverpy_env():
   """Clean the DB (keep strats/) and clear the bid cache.
   Assumes SOLVERPY_DB and SOLVERPY_BENCHMARKS are set correctly before running pytest,
   e.g.: SOLVERPY_BENCHMARKS=tests/data SOLVERPY_DB=tests/data/solverpy_db pytest
   """
   import solverpy.benchmark.path.bids as bids_mod

   for d in DB_DIR.iterdir():
      if d.name != "strats" and d.is_dir():
         shutil.rmtree(d)

   bids_mod.problems.__defaults__[0].clear()

   yield


@pytest.fixture(params=EVAL_CASES, scope="module")
def eval_case(request, solverpy_env):
   """Run evaluation (DB caches results) and return (setup, bid, sid)."""
   solver_fn, bidlist, sidlist = request.param
   setup = setups.Setup(
      limit="T1",
      bidlist=bidlist,
      sidlist=sidlist,
      options=["headless", "outputs"],
      cores=4,
   )
   solver_fn(setup)
   setups.evaluation(setup)
   setups.launch(setup)
   return setup, bidlist[0], sidlist[0]


@pytest.fixture(scope="module")
def db_results(eval_case):
   """Results dict loaded from DB: {problem: result}."""
   setup, bid, sid = eval_case
   jsons = JsonsStore(bid, sid, setup["limit"])
   return jsons.cache


@pytest.fixture(scope="module")
def db_solved(eval_case):
   """Solved set loaded from DB: set of problem names."""
   setup, bid, sid = eval_case
   solved = Solved(bid, sid, setup["limit"])
   return solved.cache


def _file_count(subdir: str, eval_case) -> int:
   setup, bid, sid = eval_case
   d = DB_DIR / subdir / bids.name(bid, limit=setup["limit"]) / sids.name(sid)
   return len(list(d.glob("*"))) if d.exists() else 0


@pytest.fixture(scope="module")
def db_output_count(eval_case):
   return _file_count("outputs", eval_case)


@pytest.fixture(scope="module")
def db_error_count(eval_case):
   return _file_count("errors", eval_case)


@pytest.fixture(scope="module")
def valid_statuses(eval_case):
   setup, _, _ = eval_case
   solver = setup["solver"]
   return solver._success | solver._timeouts


@pytest.fixture(scope="module")
def db_status(eval_case):
   """Status dict loaded from DB: {problem: 'status\truntime'}."""
   setup, bid, sid = eval_case
   status = Status(bid, sid, setup["limit"])
   return status.cache


# --- results/ ---

def test_results_file_exists(eval_case):
   setup, bid, sid = eval_case
   path = Path(JsonsStore(bid, sid, setup["limit"]).cachepath() + ".gz")
   assert path.exists()


def test_outputs_plus_errors_count(db_output_count, db_error_count):
   assert db_output_count + db_error_count == 10  # bushy010 has 10 problems


def test_results_all_have_status(db_results):
   for problem, result in db_results.items():
      assert "status" in result, f"Missing status for {problem}"


def test_results_all_have_runtime(db_results):
   for problem, result in db_results.items():
      assert "runtime" in result, f"Missing runtime for {problem}"


# --- solved/ ---

def test_solved_file_exists(eval_case):
   setup, bid, sid = eval_case
   path = Path(Solved(bid, sid, setup["limit"]).cachepath())
   assert path.exists()


def test_solved_nonempty(db_solved):
   assert len(db_solved) > 0


def test_solved_subset_of_results(db_results, db_solved):
   problem_names = {Path(p).name for p in db_results}
   assert db_solved <= problem_names


# --- status/ ---

def test_status_count(db_status, db_results):
   assert len(db_status) == len(db_results)


def test_status_values_valid(db_status, valid_statuses):
   for problem, status_runtime in db_status.items():
      status = status_runtime.split("\t")[0]
      assert status in valid_statuses, f"{problem}: unexpected status {status!r}"
