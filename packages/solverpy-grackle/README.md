# Grackle

Grackle is an automated system for invention of a set of **good-performing** and **complementary** configurations of an arbitrary parametrized algorithm.
The Grackle system was recently described here.

> Jan Hula, Jan Jakubuv, Mikolás Janota, Lukás Kubej:
> [Targeted Configuration of an SMT Solver](https://github.com/ai4reason/grackle/raw/master/grackle-paper.pdf). CICM 2022: 256-271


## Disclaimer

This is a software prototype but it is usable with some effort.
Please [contact the author](mailto:jakubuv_AT_gmail_DOT_com) to obtain help and support.

## Quick Install

Clone the repository from [Github](https://github.com/ai4reason/grackle) and install Grackle through `pip`.

```bash
git clone https://github.com/ai4reason/grackle.git
cd grackle
pip install . 
```

(This might be currently broken, follow the instructions below please.)

### Developers installation notes

This is a manual installation for developers and it is intended to be done instead of the standard `pip` installation.
First, clone the repository:

```bash
git clone https://github.com/ai4reason/grackle.git
cd grackle
```

The scripts from the directory `bin` and `paramils` must be in some `PATH` directory.  For example, run the following from the main repository directory `grackle`, or create symbolic links from some `PATH` directory pointing to the repository files in `bin` and `paramils`.

```bash
export PATH=$PATH:$PWD/bin:$PWD/paramils
```

To manually install the Grackle Python package, create a symbolic link from your local user Python packages pointing to the directory `grackle/grackle` in the repo.  This will make the development easier because you will not need to install the package again after every change in the repository.
Typically, this can be done as follows (provided you use Python 3.11, and you are in the main `grackle` repository directory):

```bash
ln -s $PWD/grackle $HOME/.local/lib/python3.11/site-packages
```

Note that the link must point to the "inner" `grackle` directory (inside the repository, `grackle/grackle`).

## Running Grackle

In order to launch Grackle, you need the following.

1. A set of benchmark problems for which you want to invent new strategies.
2. Some initial strategies to start with (at least 2).

Grackle is launched by the command `fly-grackle.py` which takes as the only parameter a configuration file
typically named `grackle.fly`.

### Configuration file `grackle.fly`

The configuration file provides all necessary information about the experiment to be run.
It contains the following fields.

```
cores = 56
tops = 50
best = 3
rank = 1
inits = greedy15
timeout = 86400
atavistic = False
selection = default

runner.prefix = lash-

trains.data = problems.ok
trains.runner = grackle.runner.lash.LashRunner
trains.runner.timeout = 1
trains.runner.penalty = 10000000
trains.runner.cores = 50

trainer = grackle.trainer.lash.paramils.LashParamilsTrainer
trainer.runner = grackle.runner.lash.LashRunner
trainer.runner.timeout = 1
trainer.runner.penalty = 10000000
trainer.timeout = 300
trainer.restarts = True
trainer.log = True
```

The first part decribes general experiment setup.

|name|description|
|-|-|
|cores|Default number of CPUs to be used (at least 2).|
|tops|The maximal number of strategies in the current generation (eg. 10)|
|best|The minimal number of problems where a strategy needs to be good-performing in order to survive (eg. 3)|
|rank|How many best strategies are good-performing on a problem (`1` means only the best strategy is good-performing, `2` means the two best strategies, etc.)|
|inits|The filename with the list of initial strategies.  The file consists of a list of strategy filenames relative to the current working directory (where you launch Grackle from).  Each strategy filename describes one solver strategy and its content is solver-specific.|
|timeout|The overall runtime limit in seconds.|
|atavistic|Use the atavistic mode (`True` or`False`).|
|selection|How to select the strategy for improvement.  Allowed values are `default`, `weak`, `random`, `mul`, `div`, `reverse`, `family` and (some of) their combinations like `weak+mul+reverse`.  The `default` is a good choice to begin with.|

Next part describes the benchmark problems and parameters for the *evaluation phase*.  The main values are:

|name|description|
|-|-|
|trains.data|Filename with the bencharks.  The file contains one problem file per line.  The problem files are relative to the current working directory.    This benchmark root directory can be adjusted by the `PYPROVE_BENCHMARKS` environment variable.|
|trains.runner|Runner to be used for the evaluation phase.  This is a fully qualified Python class path.  The runner class should be derived from `grackle.runner.runner.Runner` class.|
|trains.runner.prefix|A prefix to be used to name invented strategies of this runner.|
|trains.runner.penalty|The penalty for unsolved problems.  For solved problems, the runtime in miliseconds is (typically) used as a quality measure.  Hence the penalty should be much higher than the highest possible quality.|
|trains.runner.?|Runner specific configuration.  Typically this contains the timeout in seconds per problem.|

The final part decribes parameters for the *training phase (strategy invention)*.

|name|description|
|-|-|
|trainer|Fully qualified Python path of the trainer class.  The trainer should be derived from class `grackle.trainer.trainer.Trainer`.|
|trainer.runner|Runner to be used in the training phase.  Typically the same as `trains.runner` but with a higher timeout.|
|trainer.timeout|The timeout for the execution of one training phase in seconds.|
|trainer.?|Additional trainer-specific parameters can be specified here.|

Common parameters for both evaluation and training runners can be specified using the `runner.?` items.
Optionally, `tests.?` items (similar to `trains.?` items) can be used to define separate testing problems used to select the strategy for the training, thusly preventing overfitting.

### Examples

Example run scripts can be found in the directory `examples` in this repository for `vampire` and `lash` ATP provers.
At first, extract the benchmark problems in the file `benchmarks.tar.gz`.
Then the script `run-grackle.sh` shows how to run Grackle.
Note that the corresponding prover must be installed separately (not included in this repo).

## Grackle output and restarts

After a successful Grackle run, the final portfolio of strategies will be printed on the standard output.
All the invented strategies (including the initial strategies) can be found in the directory `confs`.

Aditionally, Grackle outputs the database of results as a JSON file `db-trains-final.json` (and `db-tests-final.json` if test problems are used).
This file contains the results of all evaluated strategies (both initial and invented).
The results of initial strategies are dumped to a JSON file `db-trains-init.json`.
When running Grackle again, this can database can be used to speedup the evaluation of initial strategies.
To achieve that, Grackle searches for a file named `db-trains-cache.json` and loads the results from this file.
Hence rename `db-trains-init.json` to `db-trains-cache.json` before restarting Grackle.

## Credits

Development of this software prototype was supported by: 

+ ERC-CZ grant no. LL1902 *POSTMAN*
+ ERC Consolidator grant no. 649043 *AI4REASON*
+ ERC Starting grant no. 714034 *SMART*
+ FWF grant P26201
+ Cost Action CA15123 *EUTypes*

