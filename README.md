# SolverPy

A generic Python interface for **evaluation** and **machine learning** of
automated theorem provers (ATPs) and Satisfiability Modulo Theories solvers
(SMTs) — a single `solverpy` shell command driven by YAML experiment files,
a results database that caches every run, and a full Python API when you
need more control.

📖 **Full documentation, install instructions, and step-by-step tutorials:
https://cbboyan.github.io/solverpy/**

## Packages

This repository is a monorepo of three packages, each installable from PyPI
independently:

| Package | Purpose |
|---|---|
| [`solverpy`](packages/solverpy) ([PyPI](https://pypi.org/project/solverpy/)) | Core solver interface, benchmark evaluation, and the results database. |
| [`solverpy-learn`](packages/solverpy-learn) ([PyPI](https://pypi.org/project/solverpy-learn/)) | Machine-learning guidance on top of `solverpy`: ENIGMA (E Prover clause selection) and cvc5ml. |
| [`solverpy-grackle`](packages/solverpy-grackle) | Configuration collection invention (algorithm configuration) for ATPs and SMT solvers. |

## Install

```sh
pip install solverpy
pip install solverpy-learn      # optional, for ML guidance
```

Solver binaries (`eprover`, `cvc5`, `z3`, ...) are not bundled — see
[Install](https://cbboyan.github.io/solverpy/install/).

## Quick taste

```sh
solverpy init eprover
solverpy run eval-eprover.yaml
```

or from Python:

```python
from solverpy.solver.smt.cvc5 import Cvc5

cvc5 = Cvc5("T5")  # time limit of 5 seconds
result = cvc5.solve("myproblem.smt2", "--enum-inst")
print(result["status"], result["runtime"])
```

See [Usage](https://cbboyan.github.io/solverpy/usage/) and
[Tutorials](https://cbboyan.github.io/solverpy/tutorials/eval-eprover/) —
including [evaluating E](https://cbboyan.github.io/solverpy/tutorials/eval-eprover/),
[evaluating cvc5](https://cbboyan.github.io/solverpy/tutorials/eval-cvc5/),
[training ENIGMA](https://cbboyan.github.io/solverpy/tutorials/enigma-training/),
and using the Python API directly — plus the full
[Commands](https://cbboyan.github.io/solverpy/commands/) reference.

## Links

- [Documentation](https://cbboyan.github.io/solverpy/)
- [Issues](https://github.com/cbboyan/solverpy/issues)
- [Changelog](https://github.com/cbboyan/solverpy/blob/main/CHANGELOG.md)
