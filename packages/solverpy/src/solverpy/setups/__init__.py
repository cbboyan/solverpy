"""
# Experiment setups

The `setups` module is the primary high-level API for configuring and launching
solver experiments.  An experiment is described by a
[`Setup`][solverpy.setups.setup.Setup] dict that is populated by a chain of
setup functions and then executed by
[`launch`][solverpy.setups.loop.launch].

```python
from solverpy import setups

setup = setups.Setup(limit="T10", bidlist=["myproblems"], sidlist=["default"])
setups.eprover(setup)      # choose solver and fill in defaults
setups.evaluation(setup)   # configure benchmark evaluation
setups.launch(setup)       # run everything
```

## Setup functions

Each solver has a corresponding setup function that sets the solver instance
and its static options in `setup`:

| Function | Solver |
|---|---|
| [`eprover(setup)`][solverpy.setups.solver.eprover] | [`E`][solverpy.solver.atp.eprover.E] (E Prover) |
| [`vampire(setup)`][solverpy.setups.solver.vampire] | [`Vampire`][solverpy.solver.atp.vampire.Vampire] |
| [`prover9(setup)`][solverpy.setups.solver.prover9] | [`Prover9`][solverpy.solver.atp.prover9.Prover9] |
| [`cvc5(setup)`][solverpy.setups.solver.cvc5] | [`Cvc5`][solverpy.solver.smt.cvc5.Cvc5] |
| [`z3(setup)`][solverpy.setups.solver.z3] | [`Z3`][solverpy.solver.smt.z3.Z3] |
| [`bitwuzla(setup)`][solverpy.setups.solver.bitwuzla] | [`Bitwuzla`][solverpy.solver.smt.bitwuzla.Bitwuzla] |

After choosing a solver, call [`evaluation`][solverpy.setups.loop.evaluation]
to configure the benchmark evaluation pipeline (DB providers, parallel cores,
strategy and benchmark id lists), then call
[`launch`][solverpy.setups.loop.launch] to execute.

"""

from .setup import Setup
from .solver import eprover, vampire, prover9, cvc5, bitwuzla, z3
from .loop import evaluation, launch

__all__ = [
   "Setup",
   "eprover",
   "vampire",
   "cvc5",
   "z3",
   "prover9",
   "bitwuzla",
   "evaluation",
   "launch",
]
