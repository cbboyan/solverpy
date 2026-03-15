from solverpy.setups import Setup, vampire, prover9, bitwuzla, z3, evaluation
from solverpy.setups import launch as _launch_base

from .solver import eprover, cvc5
from .tuner import cvc5ml, enigma
from .loop import loopinit, looping, oneloop, launch

__all__ = [
   "Setup",
   # solvers
   "eprover",
   "vampire",
   "cvc5",
   "z3",
   "prover9",
   "bitwuzla",
   # evaluation
   "evaluation",
   # ML loop
   "launch",
   "loopinit",
   "looping",
   "oneloop",
   # ML builder setup
   "cvc5ml",
   "enigma",
]
