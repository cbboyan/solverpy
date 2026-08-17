import pytest

from solverpy import setups
from solverpy.setups.setup import Setup
from solverpy.solver.plugins.shell.timeout import Timeout
from solverpy.solver.smt import Cvc5, Yices, Z3
from solverpy.solver.smt.cvc5 import CVC5_STATIC
from solverpy.solver.smt.yices import YICES_STATIC


def build(configure, limit="T30"):
   # The limit belongs to the evalset -- that is where a yml's `common:`
   # block lands once `experiment()` has merged it.
   setup = Setup(
      evals=dict(limit=limit, benchmarks=["b"], strategies=["s"]),
      options=["no-flatten", "outputs"],
   )
   configure(setup)
   return setup["evals"]["solver"]


@pytest.mark.parametrize("configure,cls", [
   (setups.cvc5, Cvc5),
   (setups.yices, Yices),
   (setups.z3, Z3),
])
def test_setup_builds_its_solver(configure, cls):
   assert isinstance(build(configure), cls)


def test_z3_sends_no_static_prefix_on_stdin():
   # Z3 is a StdinSolver, where `static` prefixes the stdin payload rather
   # than the command line, and Z3.__init__ already bakes Z3_STATIC into the
   # command.  Passing it here as well put `-smt2 -st` at the head of the
   # SMT-LIB2 stream, and z3 answered every run with a leading
   # `(error "line 1 column 1: invalid command, '(' expected")`.
   solver = build(setups.z3)

   assert solver._static == ""
   assert solver._cmd == "z3 -smt2 -st"


def test_shell_solvers_keep_their_static_on_the_command_line():
   assert build(setups.cvc5)._cmd == f"cvc5 {CVC5_STATIC}"
   assert build(setups.yices)._cmd == f"yices-smt2 {YICES_STATIC}"


def test_yices_leaves_the_limit_to_the_timeout_wrapper():
   # yices answers `unknown` on its own `--timeout`, which is a failure and
   # not a timeout for the Smt plugin, so such a result would never be
   # recomputed at a longer cutoff.  It contributes no limit flags of its own
   # and the `timeout` wrapper enforces the cutoff instead.
   solver = build(setups.yices, limit="T1200-M7")
   wrappers = [x for x in solver.decorators if isinstance(x, Timeout)]

   assert solver._limits.strategy == ""
   assert [x.timeout for x in wrappers] == [1201]
