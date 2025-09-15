"""
# Parallel benchmark evaluation

To evaluate a set of strategies on a set of benchmark problems, you just need to provide your experiment description as a Python `dict` and launch the experiments.

```python
from solverpy import setups

mysetup = ...

setups.launch(mysetup)
```

The experiment setup (`mysetup`) must have specific keys.  The module `solverpy.benchmark.setups` contains methods to fill in the required keys and values.

You must specify at least the following:

| key          | type      |   description |
|--------------|-----------|---------------|
| `cores` | `int`  | number of CPU cores to use for parallel evaluation |
| `sidlist` | `[str]` | list of strategies to evaluate |
| `bidlist` | `[str]` | list of problems to evaluate on |
| `limit` | `str` | the resource limit for a single solver run |

## Strategies and _strategy id's_

Strategies are stored in files in the directory `solverpy_db/strats` which must exist in the current working directory (the directory is adjustable by the `SOLVERPY_DB` environment variable).
The filename of each strategy is used to reference the strategy in `sidlist` and it is called the _strategy id_ (`sid`).

Hence, for every `sid` in `sidlist` in `mysetup`, there must be the file `solverpy_db/strats/sid` in the current working directory.
This file contains the strategy definition (typically command line options) to pass to the `solver.solve` method.

## Problems and _benchmark id's_

Benchmark problem sets are represented by _benchark id's_ (`bid`).  The _benchmark id_ is a file path relative to the current working directory (adjustable by the `SOLVERPY_BENCHMARKS` environment variable)
pointing either to a file or to a directory.

If the path leads to a:

* `directory`: Then every regular file _directly_ in this directory is considered a benchmark problem.
   Directories and hidden files are ignored and no recursive search is performed.
   This variant is useful when you have a set of problem files, all in one directory.
* `file`: Then the file consists of lines containing paths to corresponding problem files.
   The paths are relative to the directory of the `bid` file.  For example, if  the `bid` is `my/problems/subset1` and this file contains (among others) the line `category1/problem23.smt2` then the problem must be placed in `my/problems/category1/problem23.smt2` (because the directory of the `bid` file is `my/problems`).
   This variant is useful when your benchmarks are structured in subdirectories and you don't want to merge them into one directory.

## Experiments example

Suppose you have some SMT problems in the directory `myproblems` and that you want to evaluate your cvc5 strategies `buzzard`, `sparrow`, and `chickadee`, which you have placed in the directory `solverpy_db/strats`.  You can download the archive with files for this example [here](https://github.com/cbboyan/solverpy/raw/main/docs/example.tar.gz).

You proceed as follows.  First, you create the description of your experiments in `mysetup`.

```python
from solverpy import setups

mysetup = {
    "cores": 4,
    "limit": "T10",
    "bidlist": ["myproblems"],
    "sidlist": ["buzzard", "sparrow", "chickadee"],
}
```

Hint: Add `mysetup["options"] = ["outputs"]` if you want to keep raw solver output files from all solver runs.  

Hint: Options are slightly more described in [`Setup`][solverpy.setups.setup.Setup]

Then you specify that you want to use cvc5 and that you wish to launch an evaluation.  These methods update `mysetup` and fill in some keys required by `setups.launch()`.

```python
setups.cvc5(mysetup)
setups.evaluation(mysetup)
```

Finally, you launch the experiments.

```python
setups.launch(mysetup)
```

You will see the progress of the experiments on the screen.  Once finished, you will find the following subdirectories inside `solverpy_db`:

| directory |  content |
|--------------|-----------|
| `results` | Results by each strategy (`sid`) for each `bid`.  The result for each `sid` and `bid` is a JSON file (gzip-ed) with a Python dictionary `{problem: result}`. |
| `solved` | List of solved problem names by each strategy for each `bid`.  One per line, easy to `grep` and `cat`. |
| `status` | Statuses of all problems by each strategy for each `bid`.  Problem name and status at one line, TAB separated.  Easy to `cut`. |
| `log` | Console log for each `solverpy` experiment run. |
| `outputs` | Raw solver output files for each solver run (only if selected). |

Now run the script again and notice that it finished much faster.  It is because the cached results were reused and no solvers were actually launched.  So be careful and always clean the database if you want to force recompute.  Simply delete all the directories in `solverpy_db` except `strats` (see the script `clean_db.sh` in the [example archive](https://github.com/cbboyan/solverpy/raw/main/docs/example.tar.gz)).

"""
