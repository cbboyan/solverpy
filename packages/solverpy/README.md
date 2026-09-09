# solverpy

`solverpy` is a generic Python interface for **evaluating** automated
theorem provers (ATPs) and SMT solvers — [`E`](https://cbboyan.github.io/solverpy/tutorials/eval-eprover/),
[`Vampire`](https://cbboyan.github.io/solverpy/api/solverpy/solver/atp/vampire/),
[`Prover9`](https://cbboyan.github.io/solverpy/api/solverpy/solver/atp/prover9/),
[`Lash`](https://cbboyan.github.io/solverpy/api/solverpy/solver/atp/lash/),
[`cvc5`](https://cbboyan.github.io/solverpy/tutorials/eval-cvc5/),
[`Z3`](https://cbboyan.github.io/solverpy/api/solverpy/solver/smt/z3/),
[`Opensmt`](https://cbboyan.github.io/solverpy/api/solverpy/solver/smt/opensmt/),
and more — through a single `solverpy` shell command driven by YAML
experiment files, a results database that caches every run, and a full
Python API when you need more control.

📖 **Full documentation, install instructions, and step-by-step tutorials:
https://cbboyan.github.io/solverpy/**

For machine-learning-guided strategies (ENIGMA, cvc5ml), see the companion
[`solverpy-learn`](https://pypi.org/project/solverpy-learn/) package.

## Install

```sh
pip install solverpy
```

Solver binaries (`eprover`, `cvc5`, ...) are not bundled — see
[Install](https://cbboyan.github.io/solverpy/install/) for details.

## Quick taste

```python
from solverpy.solver.smt.cvc5 import Cvc5

cvc5 = Cvc5("T5")  # time limit of 5 seconds
result = cvc5.solve("myproblem.smt2", "--enum-inst")
print(result["status"], result["runtime"])
```

Or, without writing any Python:

```sh
solverpy init eprover
solverpy run eval-eprover.yaml
```

See [Usage](https://cbboyan.github.io/solverpy/usage/) and
[Tutorials](https://cbboyan.github.io/solverpy/tutorials/eval-eprover/) for
the rest — benchmark evaluation, the `sid`/`bid` concepts, and the full
[Commands](https://cbboyan.github.io/solverpy/commands/) reference.

## Links

- [Source](https://github.com/cbboyan/solverpy)
- [Issues](https://github.com/cbboyan/solverpy/issues)
- [Changelog](https://github.com/cbboyan/solverpy/blob/main/CHANGELOG.md)
