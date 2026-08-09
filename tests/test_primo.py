from solverpy.solver.smt.primo import PRIMO_STATIC, Primo


STATS = """\
%%% INSTANCE bouncing-ball-inv-node1886.smt2
%%% STRATEGY --lra-pivoting-rule soi
%%% COMMAND: timeout 6 primo --quiet --stats --lra-pivoting-rule soi bb.smt2
unsat
:input.assertions 1
:preprocessing.real-equality-lowering.lowered 2
:preprocessing.solve-eqs.rejected-cycles 0
:sat.conflicts 1
:sat.propagations 2
:lra.tableau-vars 6
:euf.incremental.merges 17
:euf.ackermann.symbols-cost-le-100 3
:time.total-us 233
"""


def test_static_enables_stats():
   assert "--stats" in PRIMO_STATIC.split()


def test_static_is_quiet():
   # Without --quiet the startup banner goes to stderr, which the shell solver
   # merges into the same stream the statistics are parsed from.
   assert "--quiet" in PRIMO_STATIC.split()


def test_process_stats():
   result = Primo("T5").process(STATS)

   assert result == {
      "input.assertions": 1,
      "preprocessing.real-equality-lowering.lowered": 2,
      "sat.conflicts": 1,
      "sat.propagations": 2,
      "lra.tableau-vars": 6,
      "euf.incremental.merges": 17,
      "euf.ackermann.symbols-cost-le-100": 3,
      "time.total-us": 233,
   }


def test_process_drops_zeros():
   # primo prints every counter it tracks; around 86% are zero on any one
   # instance, and a missing key already reads as zero because primo omits
   # families it never reached.
   result = Primo("T5").process(STATS)

   assert "preprocessing.solve-eqs.rejected-cycles" not in result
   assert 0 not in result.values()


def test_process_ignores_non_statistics():
   # The status line and the header the shell solver prepends must not be
   # mistaken for statistics.
   result = Primo("T5").process(STATS)

   assert not any(key.startswith("%") for key in result)
   assert "unsat" not in result


def test_command_appends_strategy_and_instance():
   cmd = Primo("T5").command("inst.smt2", "--theory-phase none")

   assert cmd.endswith("primo --quiet --stats --theory-phase none inst.smt2")
