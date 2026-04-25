"""Tests for TPTP proof extraction and the Proofs plugin."""

import gzip
import pytest
from pathlib import Path

from solverpy.solver.plugins.db.proofs import extract, Proofs
from solverpy.solver.atp.eprover import E
from solverpy.solver.atp.vampire import Vampire

PROOFS = Path(__file__).parent / "data" / "proofs"
EPROVER_OUT = PROOFS / "agatha-eprover.out"
VAMPIRE_OUT = PROOFS / "agatha-vampire.out"

DATA = Path(__file__).parent / "data" / "problems"
BID = "bushy010"
PROBLEM = "finset_1__t13_finset_1.p"
STRATEGY = ""

AGATHA_PREMISES = {
   "pel55", "pel55_1", "pel55_3", "pel55_4", "pel55_5",
   "pel55_6", "pel55_7", "pel55_8", "pel55_9", "pel55_10", "pel55_11",
}


# --- extract() unit tests ---

def test_extract_eprover():
   assert set(extract(EPROVER_OUT.read_text())) == AGATHA_PREMISES


def test_extract_vampire():
   assert set(extract(VAMPIRE_OUT.read_text())) == AGATHA_PREMISES


def test_extract_no_szs_block():
   assert extract("no proof here") == []


def test_extract_empty_proof():
   assert extract("% SZS output start Proof\n% SZS output end Proof") == []


def test_extract_deduplicates():
   output = "% SZS output start P\nfile('f.p', ax1)\nfile('f.p', ax1)\n% SZS output end P"
   assert extract(output) == ["ax1"]


def test_extract_order_preserved():
   output = "% SZS output start P\nfile('f.p', ax2)\nfile('f.p', ax1)\n% SZS output end P"
   assert extract(output) == ["ax2", "ax1"]


def test_extract_space_variants():
   output = "% SZS output start P\nfile('f.p',ax1)\nfile('f.p', ax2)\n% SZS output end P"
   assert extract(output) == ["ax1", "ax2"]


# --- integration helpers ---

def _run(solver_cls, bid, problem, strategy=STRATEGY, **kwargs):
   from solverpy.solver.plugins.db.bid import Bid
   plugin = Proofs(**kwargs)
   solver = solver_cls("T5", plugins=[Bid(), plugin])
   result = solver.solve((bid, problem), strategy)
   return solver, result, plugin


# --- proof saving (compressed by default) ---

def test_eprover_proof_file_written():
   if not E.available():
      pytest.skip("eprover binary not found")
   solver, result, plugin = _run(E, BID, PROBLEM)
   assert solver.valid(result)
   gz = Path(plugin.proof_path((BID, PROBLEM), STRATEGY) + ".gz")
   try:
      assert gz.exists()
      content = gzip.decompress(gz.read_bytes()).decode()
      assert "SZS output start" in content
      assert "SZS output end" in content
   finally:
      gz.unlink(missing_ok=True)


def test_vampire_proof_file_written():
   if not Vampire.available():
      pytest.skip("vampire binary not found")
   solver, result, plugin = _run(Vampire, BID, PROBLEM)
   assert solver.valid(result)
   gz = Path(plugin.proof_path((BID, PROBLEM), STRATEGY) + ".gz")
   try:
      assert gz.exists()
      content = gzip.decompress(gz.read_bytes()).decode()
      assert "SZS output start" in content
      assert "SZS output end" in content
   finally:
      gz.unlink(missing_ok=True)


def test_proof_uncompressed():
   if not E.available():
      pytest.skip("eprover binary not found")
   solver, result, plugin = _run(E, BID, PROBLEM, compress=False)
   assert solver.valid(result)
   p = Path(plugin.proof_path((BID, PROBLEM), STRATEGY))
   try:
      assert p.exists()
      assert "SZS output start" in p.read_text()
   finally:
      p.unlink(missing_ok=True)


# --- premises saving (never compressed) ---

def test_eprover_premises_file_written():
   if not E.available():
      pytest.skip("eprover binary not found")
   solver, result, plugin = _run(E, BID, PROBLEM, premises=True)
   assert solver.valid(result)
   p = Path(plugin.premises_path((BID, PROBLEM), STRATEGY))
   try:
      assert p.exists()
      names = p.read_text().strip().split("\n")
      assert len(names) > 0
      assert all(n.strip() for n in names)
   finally:
      p.unlink(missing_ok=True)


def test_vampire_premises_file_written():
   if not Vampire.available():
      pytest.skip("vampire binary not found")
   solver, result, plugin = _run(Vampire, BID, PROBLEM, premises=True)
   assert solver.valid(result)
   p = Path(plugin.premises_path((BID, PROBLEM), STRATEGY))
   try:
      assert p.exists()
      names = p.read_text().strip().split("\n")
      assert len(names) > 0
      assert all(n.strip() for n in names)
   finally:
      p.unlink(missing_ok=True)


# --- guard: non-tuple instance ---

def test_proofs_skipped_on_non_tuple_instance():
   """Proofs must not crash when instance is a plain path (no Bid translator)."""
   if not E.available():
      pytest.skip("eprover binary not found")
   problem = str(DATA / "agatha.p")
   plugin = Proofs(proof=True, premises=True)
   solver = E("T5", plugins=[plugin])
   result = solver.solve(problem, STRATEGY)
   assert solver.valid(result)
   assert not Path(plugin.proof_path((".", problem), STRATEGY) + ".gz").exists()
