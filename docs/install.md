# 📥 Install

## ◆ From PyPI

```sh
$ pip install solverpy
```

This installs the core `solverpy` package — the solver interface, benchmark
evaluation, and the results database — together with the `solverpy`
command-line tool.

Add `solverpy-learn` for machine-learning guidance (ENIGMA, cvc5ml):

```sh
$ pip install solverpy-learn
```

## ◆ From source (GitHub)

Clone the repository:

```sh
$ git clone https://github.com/cbboyan/solverpy.git
$ cd solverpy
```

The repository is a monorepo of packages under `packages/`: `solverpy`,
`solverpy-learn`, and `solverpy-grackle`. Install the ones you need in
editable mode, so source edits take effect immediately:

```sh
$ pip install -e packages/solverpy
$ pip install -e packages/solverpy-learn   # optional, for ML guidance
```

Or build a distributable package for one of them:

```sh
$ cd packages/solverpy
$ python3 -m build
```

## ◆ Solver binaries

SolverPy does not bundle any solver binaries or libraries — install them
separately (e.g. `eprover`, `cvc5`, `z3`, `opensmt`, ...). By default,
SolverPy looks each one up on `PATH`; to use a binary that is not on `PATH`,
pass its full path via the `binary` parameter of `Setup` in the Python API,
or a `binary:` key in a YAML experiment file.

## ◆ Verify

```sh
$ solverpy --help
```
