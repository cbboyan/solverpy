from solverpy.solver.smt.yices import YICES_BINARY, YICES_STATIC, Yices


STATS = """\
%%% INSTANCE php8.smt2
%%% STRATEGY --arith-solver=simplex
%%% COMMAND: timeout 6 yices-smt2 --stats --arith-solver=simplex php8.smt2
unsat
(
 :num-terms 266
 :total-run-time 0.022
 :mem-usage 4.758
 :boolean-variables 57
 :clause-db-simplify 1
 :conflicts 4879
 :theory-conflicts 0
 :egraph-ackermann-lemmas 0
 :simplex-pivots 0
)
"""

MCSAT_STATS = """\
%%% INSTANCE nra.smt2
%%% STRATEGY --mcsat
%%% COMMAND: timeout 6 yices-smt2 --stats --mcsat nra.smt2
sat
(
 :mcsat::bv::explain::full_bv_sat.propagation 3
 :mcsat::na::constraints_regular 1
 :mcsat::uf::avg_conflict_size 0.0000
 :mcsat::decisions 1
)
"""


def test_static_enables_stats():
   assert "--stats" in YICES_STATIC.split()


def test_binary_is_the_smtlib_frontend():
   # The plain `yices` binary reads the Yices native language and rejects an
   # SMT-LIB2 file with a syntax error on `set-logic`.
   assert YICES_BINARY == "yices-smt2"


def test_process_stats():
   result = Yices("T5").process(STATS)

   assert result == {
      "num-terms": 266,
      "total-run-time": 0.022,
      "mem-usage": 4.758,
      "boolean-variables": 57,
      "clause-db-simplify": 1,
      "conflicts": 4879,
   }


def test_process_drops_zeros():
   # yices prints only the counters of the solver components it built, so a
   # missing key already reads as zero -- a QF_AUFBV run reports four keys and
   # no `simplex-*` or `egraph-*` family at all.
   result = Yices("T5").process(STATS)

   assert "theory-conflicts" not in result
   assert "egraph-ackermann-lemmas" not in result
   assert 0 not in result.values()


def test_process_ignores_non_statistics():
   # The status line, the parentheses of the statistics block, and the header
   # the shell solver prepends must not be mistaken for statistics.
   result = Yices("T5").process(STATS)

   assert not any(key.startswith("%") for key in result)
   assert "unsat" not in result


def test_process_mcsat_keys():
   # MCSat keys add `::`, `_` and `.` to the `-` of the core statistics.
   result = Yices("T5").process(MCSAT_STATS)

   assert result == {
      "mcsat::bv::explain::full_bv_sat.propagation": 3,
      "mcsat::na::constraints_regular": 1,
      "mcsat::decisions": 1,
   }


def test_command_appends_strategy_and_instance():
   cmd = Yices("T5").command("inst.smt2", "--mcsat")

   assert cmd.endswith("yices-smt2 --stats --mcsat inst.smt2")


def test_command_has_no_solver_timeout():
   # yices answers `unknown` on its own `--timeout`, which is a failure and
   # not a timeout for the Smt plugin, so it would never be recomputed at a
   # longer cutoff.  The shell `timeout` wrapper enforces the limit instead.
   cmd = Yices("T5").command("inst.smt2", "")

   assert "--timeout" not in cmd
   assert cmd.startswith("timeout --kill-after=15 --foreground 6 ")
