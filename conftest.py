import os
import pytest
from pathlib import Path

DATA_DIR = Path(__file__).parent / "tests" / "data" / "problems"
DB_DIR   = Path(__file__).parent / "tests" / "data" / "solverpy_db"


@pytest.fixture(autouse=True, scope="session")
def solverpy_test_env():
   """Set SOLVERPY_BENCHMARKS and SOLVERPY_DB to the canonical test data
   directories for the entire test session, overriding any external values."""
   prev_benchmarks = os.environ.get("SOLVERPY_BENCHMARKS")
   prev_db         = os.environ.get("SOLVERPY_DB")

   os.environ["SOLVERPY_BENCHMARKS"] = str(DATA_DIR)
   os.environ["SOLVERPY_DB"]         = str(DB_DIR)

   yield

   if prev_benchmarks is None:
      os.environ.pop("SOLVERPY_BENCHMARKS", None)
   else:
      os.environ["SOLVERPY_BENCHMARKS"] = prev_benchmarks
   if prev_db is None:
      os.environ.pop("SOLVERPY_DB", None)
   else:
      os.environ["SOLVERPY_DB"] = prev_db
