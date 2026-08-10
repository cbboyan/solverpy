from solverpy.solver.smt.opensmt import OPENSMT_STATIC, Opensmt


# Real output of a release opensmt, with the header lines the shell solver
# prepends.  Note there are no statistics: they are compiled out unless the
# `STATISTICS` cmake option is on, which defaults to OFF.
SAT = """\
%%% INSTANCE bouncing-ball.smt2
%%% STRATEGY --produce-models
%%% COMMAND: timeout 11 opensmt --produce-models bouncing-ball.smt2
sat
((x (/ 7 8))(y (/ 21 8)))
"""

UNSAT = """\
%%% INSTANCE unsat-cone.smt2
%%% STRATEGY
%%% COMMAND: timeout 11 opensmt  unsat-cone.smt2
unsat
"""

# opensmt answers `unknown` when it does not decide, e.g. under `-d` (dry run).
UNKNOWN = """\
%%% INSTANCE bouncing-ball.smt2
%%% STRATEGY -d
%%% COMMAND: timeout 11 opensmt -d bouncing-ball.smt2
unknown
"""


def solved(sid, output):
   """Run the plugin's parsing path without invoking the binary.

   `command` is what primes the Time plugin (it calls `decorate`), so it has
   to come before `update` or the timing snapshot is missing.
   """
   solver = Opensmt("T10")
   solver.command("instance.smt2", sid)
   result = solver.process(output)
   solver.update("instance.smt2", sid, output, result)
   return (solver, result)


def test_static_is_empty():
   # opensmt has no `--stats` and prints no banner, so unlike primo there is
   # nothing to pass on every run.
   assert OPENSMT_STATIC.split() == []


def test_command_appends_strategy_and_instance():
   cmd = Opensmt("T5").command("inst.smt2", "--theory-phase none")

   assert cmd.endswith("opensmt --theory-phase none inst.smt2")


def test_command_without_strategy_ends_with_instance():
   # An empty sid means opensmt's own defaults; no stray option may appear.
   cmd = Opensmt("T5").command("inst.smt2", "")

   assert cmd.endswith("inst.smt2")
   assert "--" not in cmd.split("opensmt")[-1]


def test_process_returns_no_statistics():
   # A release opensmt emits none, so `process` has nothing to contribute and
   # the whole result comes from the plugins.
   assert Opensmt("T5").process(SAT) == {}


def test_process_ignores_header_and_status():
   # The header the shell solver prepends and the status token must not be
   # mistaken for data.
   result = Opensmt("T5").process(SAT)

   assert not any(key.startswith("%") for key in result)
   assert "sat" not in result


def test_status_sat():
   (_, result) = solved("--produce-models", SAT)

   assert result["status"] == "sat"


def test_status_unsat():
   (_, result) = solved("", UNSAT)

   assert result["status"] == "unsat"


def test_status_unknown():
   (solver, result) = solved("-d", UNKNOWN)

   assert result["status"] == "unknown"
   assert not solver.solved(result)


def test_result_is_valid():
   # `valid` needs both `status` and `runtime`; with `process` empty they come
   # from the Smt and Time plugins, and `limit` from Limiter.
   (solver, result) = solved("", UNSAT)

   assert solver.valid(result)
   assert solver.solved(result)
   assert result["limit"] == "T10"
   assert "runtime" in result


def test_status_sets_registered():
   solver = Opensmt("T5")

   assert {"sat", "unsat"} <= solver.success
   assert "TIMEOUT" in solver.timeouts
   assert "unknown" not in solver.success


def test_incomplete_drops_sat_from_success():
   solver = Opensmt("T5", complete=False)

   assert "sat" not in solver.success
   assert "unsat" in solver.success


def test_setup_function_registered():
   # `evaluate: opensmt` in a YAML scenario resolves through `getattr`.
   from solverpy import setups

   assert callable(getattr(setups, "opensmt", None))
