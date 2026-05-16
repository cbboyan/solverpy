# Python Interface for Automated Solvers

`SolverPy` provides a uniform Python interface for several automated ATP and SMT solvers.

```plantuml name="solverpy-solvers"
abstract class solverpy.solver.SolverPy {
  {abstract} # statuses : set[Status]
  --
  {abstract} + solve(instance, strategy) : Result
  + solved(result) : bool
}

class solverpy.solver.atp.eprover.E extends solverpy.solver.SolverPy
class solverpy.solver.atp.vampire.Vampire extends solverpy.solver.SolverPy
class solverpy.solver.atp.lash.Lash extends solverpy.solver.SolverPy
class solverpy.solver.atp.prover9.Prover9 extends solverpy.solver.SolverPy

class solverpy.solver.smt.cvc5.Cvc5 extends solverpy.solver.SolverPy
class solverpy.solver.smt.z3.Z3 extends solverpy.solver.SolverPy
class solverpy.solver.smt.bitwuzla.Bitwuzla extends solverpy.solver.SolverPy
```

Currently supported solvers are 
[`E`][solverpy.solver.atp.eprover],
[`Vampire`][solverpy.solver.atp.vampire],
[`Prover9`][solverpy.solver.atp.prover9],
[`Lash`][solverpy.solver.atp.lash],
[`cvc5`][solverpy.solver.smt.cvc5],
[`Z3`][solverpy.solver.smt.z3],
and [`Bitwuzla`][solverpy.solver.smt.bitwuzla].

The interface can be used for:

💡 _Solving a single problem_ instance with compatible results.  
🔧 _Benchmark parallel evaluation_ with database storage.  
🧠 _Machine learning_ of models and strategies for solver guidance.  

## Installation

Install the Python package using `pip`:

```sh
$ pip install solverpy
```

Or clone our [GitHub repository](https://github.com/cbboyan/solverpy):

```sh
$ git clone https://github.com/cbboyan/solverpy.git
```

> 🗒️ **Note**: The solver binaries/libraries are not part of this Python
> package and must be installed separately.  The binaries must be (by default)
> in `PATH` or specified using `binary` parameter in `Setup`, if you wish to use them from
> `solverpy`.

## Overview

### 💡 Single problem solving

Single problem solving involves creating a solver object and calling its
`solve` method.

```python
from solverpy.solver.smt.cvc5 import Cvc5

cvc5 = Cvc5("T5")  # time limit of 5 seconds
result = cvc5.solve("myproblem.smt2", "--enum-inst") # problem and strategy
```

_Strategies_ are solver-specific, typically command line options as a string.

> ☕ The _result_ is a dictionary guaranteed to contain at least two keys: `status` as a string
> and `runtime` in seconds, apart from solver-specific keys.

😎 For more details, see the [`solver`][solverpy.solver] module.

### 🔧 Benchmark evaluation

SolverPy provides dataclass [`Setup`][solverpy.setups.setup] that describes the evaluation configuration.
It auromatically connects to database [`DB`][solverpy.benchmark.db.db] to store results, by default, using the [`Jsons`][solverpy.benchmark.db.providers.jsons] provider.

```plantuml name="solverpy-benchmark"
dataclass solverpy.setups.Setup {
   + benchmarks : list[Bid] 
   + strategies : list[Sid] 
   + cores : int
   + limit : str
   --
   }
   circle solverpy.setups.evaluation
   circle solverpy.setups.eprover
   circle solverpy.setups.cvc5

   class solverpy.benchmark.db.DB {
      # providers : Providers
      --
      + commit()
      + connect(benchmark, strategy)
      + query(tasks) : Results
      + store(tasks, results)
}

solverpy.setups.Setup <-- solverpy.setups.evaluation
solverpy.setups.Setup <-- solverpy.setups.eprover
solverpy.setups.Setup <-- solverpy.setups.cvc5

solverpy.setups.Setup -right-o "1" solverpy.benchmark.db.DB
```

To evaluate a set of strategies on a set of benchmark problems, you just need to provide your experiment description as a Python `dict`.

> 💡 Use typed version [`Setup`][solverpy.setups.setup] to avoid typos and type errors.

Functions from the [`setups`][solverpy.setups] module are used to fill in the required keys and values.
To run the evaluation you setup a solver for an evaluation, then launch it.

> 🤞 Before launching the evaluation, you need to setup the SolverPy database
> by creating directories `solverpy_db/strats` in the current directory. This
> directory stores the strategy files. For the above example, there should be
> an empty file `solverpy_db/strats/default` (default cvc5 strategy). The
> problem files should be in `problems/` directory.

```python
from solverpy import setups

mysetup = setups.Setup(
    cores=4,
    benchmarks=["problems"],
    strategies=["default"],
    limit='T10',
)

setups.cvc5(mysetup)
setups.evaluation(mysetup)

setups.launch(mysetup)
```

> ☕ After the evaluation, you can inspect the results in the database
> directory `solverpy_db/results`.

😎 For more details, see the [`benchmark`][solverpy.benchmark] module.

### 🧠 Machine learning

Similarly, you can use the [`enigma`][solverpy.builder.enigma] and [`cvc5ml`][solverpy.builder.cvc5ml] 
from [`setups`][solverpy.setups] module.
to setup several loops of
interleaved evaluation and model training.

```plantuml name="solverpy-ml"
dataclass solverpy.setups.Setup {
   + strategies : list[Sid]
   + dataname : str
   + loops : int
   ...
   --
}
circle solverpy.setups.enigma
circle solverpy.setups.cvc5ml

abstract class solverpy.builder.Builder {
   {abstract} + strategies : list[Sid]
   # dataname : str
   {abstract} + build()
   {abstract} + apply(sid, model) : list[Sid]
   + path() : str
}
  
class solverpy.builder.Enigma extends solverpy.builder.Builder {
   + build()
   + apply(..) 
}

class solverpy.builder.Cvc5ML extends solverpy.builder.Builder {
   + build()
   + apply(..)
}

solverpy.setups.Setup <-- solverpy.setups.enigma
solverpy.setups.Setup <-- solverpy.setups.cvc5ml

solverpy.builder.Builder "1" o-left solverpy.setups.Setup
```

😎 For more details, see the [`builder`][solverpy.builder] module.
