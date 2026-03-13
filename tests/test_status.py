from solverpy.solver.plugins.status.tptp import TPTP_STATUS, TPTP_OK, TPTP_TIMEOUT
from solverpy.solver.plugins.status.smt import SMT_STATUS, SMT_OK, SMT_TIMEOUT
from solverpy.tools.patterns import single


# --- TPTP status parsing ---

def test_tptp_theorem():
   output = "% SZS status Theorem for problem.p"
   assert single(TPTP_STATUS, output, "") == "Theorem"


def test_tptp_unsatisfiable():
   output = "% SZS status Unsatisfiable for problem.p"
   assert single(TPTP_STATUS, output, "") == "Unsatisfiable"


def test_tptp_hash_prefix():
   output = "# SZS status GaveUp for problem.p"
   assert single(TPTP_STATUS, output, "") == "GaveUp"


def test_tptp_timeout():
   output = "% SZS status ResourceOut for problem.p"
   assert single(TPTP_STATUS, output, "") == "ResourceOut"


def test_tptp_no_status():
   assert single(TPTP_STATUS, "solver output without status", "") == ""


def test_tptp_multiline():
   output = "some preamble\n% SZS status Theorem for p\nsome output"
   assert single(TPTP_STATUS, output, "") == "Theorem"


def test_tptp_ok_set():
   assert "Theorem" in TPTP_OK
   assert "Unsatisfiable" in TPTP_OK
   assert "GaveUp" not in TPTP_OK


def test_tptp_timeout_set():
   assert "ResourceOut" in TPTP_TIMEOUT
   assert "Timeout" in TPTP_TIMEOUT
   assert "TIMEOUT" in TPTP_TIMEOUT  # simulated


# --- SMT status parsing ---

def test_smt_sat():
   assert single(SMT_STATUS, "sat\n", "") == "sat"


def test_smt_unsat():
   assert single(SMT_STATUS, "unsat\n", "") == "unsat"


def test_smt_unknown():
   assert single(SMT_STATUS, "unknown\n", "") == "unknown"


def test_smt_timeout():
   assert single(SMT_STATUS, "timeout\n", "") == "timeout"


def test_smt_no_match_partial():
   # "satisfiable" should not match "sat"
   assert single(SMT_STATUS, "satisfiable\n", "") == ""


def test_smt_no_status():
   assert single(SMT_STATUS, "solver crashed\n", "") == ""


def test_smt_ok_set():
   assert "sat" in SMT_OK
   assert "unsat" in SMT_OK
   assert "unknown" not in SMT_OK


def test_smt_timeout_set():
   assert "timeout" in SMT_TIMEOUT
   assert "TIMEOUT" in SMT_TIMEOUT  # simulated
