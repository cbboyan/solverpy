from solverpy.solver.smt.llm2smt import LLM2SMT_STATIC, Llm2smt


STATS = """\
unsat
[stats]
  -- timing (ms) --
  total_ms                      30
  preproc.flush_ms              0
  preproc.finite_domain_amo     204
  -- euf theory --
  euf.assignments               58149
  euf.conflicts                 2087
  euf.prop_candidates_considered4687
"""


def test_static_enables_stats():
   assert "--stats" in LLM2SMT_STATIC.split()


def test_process_stats():
   result = Llm2smt("T5").process(STATS)

   assert result == {
      "total_ms": 30,
      "preproc.flush_ms": 0,
      "preproc.finite_domain_amo": 204,
      "euf.assignments": 58149,
      "euf.conflicts": 2087,
      "euf.prop_candidates_considered": 4687,
   }
