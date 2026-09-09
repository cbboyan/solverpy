# solverpy-learn

`solverpy-learn` adds machine-learning-guided strategies on top of
[`solverpy`](https://pypi.org/project/solverpy/): **ENIGMA** trains
E Prover's clause-selection models, and **cvc5ml** trains ML-enhanced cvc5
strategies, both as an iterative evaluate → train → re-evaluate loop driven
by the same `solverpy` YAML experiment files.

📖 **Full documentation, and a complete ENIGMA training walkthrough:
https://cbboyan.github.io/solverpy/tutorials/enigma-training/**

(General `solverpy` usage — installing solver binaries, the `sid`/`bid`
concepts, plain evaluation — lives on the main
[solverpy documentation site](https://cbboyan.github.io/solverpy/).)

## Install

```sh
pip install solverpy-learn
```

Training requires an `eprover-ho` binary built with ENIGMA's ML features
(for `enigma`) or a `cvc5` binary (for `cvc5ml`); see
[Install](https://cbboyan.github.io/solverpy/install/).

## Quick taste

```yaml
loop: enigma
strategy: mzr02

sel_features: "C(l,x,s,r,v[b=2048],h,c,d,t,a):M:F:S:G"
loops: 3

common:
  limit: T5
  cores: 4
  binary: eprover-ho

evals:
  dataname: enigma/train
  benchmarks:
    - problems/mine
```

```sh
solverpy run loop-eprover-enigma.yaml
```

See [Training ENIGMA](https://cbboyan.github.io/solverpy/tutorials/enigma-training/)
for the full walkthrough (preparing problems, picking a base strategy,
reading the results), and
[Commands](https://cbboyan.github.io/solverpy/commands/) for the
`solverpy tune`/`compress`/`decompress`/`deconflict`/`filter` training-data
subcommands this package adds.

## Links

- [Source](https://github.com/cbboyan/solverpy)
- [Issues](https://github.com/cbboyan/solverpy/issues)
- [Changelog](https://github.com/cbboyan/solverpy/blob/main/CHANGELOG.md)
