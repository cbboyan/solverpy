# ⌨️ Commands

Reference for the `solverpy` command-line tool. Run `solverpy --help` or
`solverpy <command> --help` for the same information from the terminal.

## ◆ `solverpy init [solver]`

Create `solverpy_db/strats/` in the current directory and populate it with
bundled example strategies. With `solver` (e.g. `eprover`, `cvc5`), only that
solver's strategies are copied (with the `<solver>-` filename prefix
stripped) and a starter `eval-<solver>.yaml` is written next to
`solverpy_db/`. Without an argument, strategies for every bundled solver are
copied, keeping their full `<solver>-<name>` filenames.

## ◆ `solverpy run FILE`

Load a YAML experiment file and run it. The file's top-level keys map
directly onto [`Setup`][solverpy.setups.setup.Setup]/[`Evalset`][solverpy.setups.evalset.Evalset]:

| Key | Meaning |
|---|---|
| `evaluate: <solver>` | Run a plain evaluation with this solver (`eprover`, `cvc5`, `vampire`, `prover9`, `bitwuzla`, `z3`, `llm2smt`, `opensmt`, `primo`, `spasssatt`, `yices`). |
| `loop: <type>` | Run an ML training loop instead of a plain evaluation (`enigma` or `cvc5ml`, from `solverpy-learn`); requires a `strategy:` key naming the base sid. |
| `common:` | Settings shared by `evals` and `devels` (e.g. `limit`, `cores`, `binary`). |
| `evals:` | The evaluation (or training) benchmark set: `benchmarks:` (list of `bid`s) and `strategies:` (list of `sid`s), plus optional `dataname:`. |
| `devels:` | A second, development benchmark set — used by ML loops to evaluate the model being trained. |
| `options:` | Boolean experiment options — see below. |

Exactly one of `evaluate:` or `loop:` must be present. See
[Tutorials](tutorials/eval-eprover.md) for `evaluate:` walkthroughs and
[Training an ENIGMA model](tutorials/enigma-training.md) for a `loop:`
walkthrough.

### ▹ Options

Each entry under `options:` is a boolean flag identified by name; prefix
with `no-` to turn it off (e.g. `no-flatten`).

| option | description | default |
|---|---|---|
| `outputs` | Keep raw solver output files from all runs. | no |
| `compress` | Compress output files (outputs, trains, results). | yes |
| `flatten` | Put all output files in a single directory (replace `/` with `_._`). | yes |
| `compress-trains` | Compress trains. | yes |
| `debug-trains` | Dump training data for each file separately. | no |
| `proofs` | Store proof objects in the database. | no |
| `premises` | Store premise selections in the database. | no |
| `headless` | Suppress progress bars and interactive UI (for non-terminal use). | no |

### ▹ The database

Every run writes into `solverpy_db/` (path overridable via `SOLVERPY_DB`):

| directory | content |
|---|---|
| `strats/` | Strategy files (input, not written by `run`). |
| `results/` | Gzip JSON `{problem: result}` dict, per `sid`/`bid`. |
| `solved/` | List of solved problem names, one per line. |
| `status/` | `problem<TAB>status<TAB>runtime` lines, one per line. |
| `logs/` | Console log and Markdown report per `solverpy run` invocation. |
| `outputs/` | Raw solver stdout per run (only with the `outputs` option). |
| `proofs/`, `premises/` | Proof objects / premise selections (only with the `proofs`/`premises` options). |
| `trains/`, `models/` | Training data and trained models (ML loops only). |

## ◆ `solverpy clean`

Delete every subdirectory of `solverpy_db/` except `strats/` (i.e. clear
cached results, logs, and outputs, but keep your strategy files). Prompts
for confirmation unless `-y`/`--yes`/`-f`/`--force` is given.

## ◆ `solverpy report FILE.md [-o FILE.html]`

Convert a `solverpy_db/logs/*.md` experiment report into a self-contained,
offline HTML page (default output: same name with `.html`).

## ◆ `solverpy esid2strat INPUT`

Convert `eprover-ho --print-strategy=<name>` output into the equivalent
`eprover` command-line arguments — useful for turning an ENIGMA-selected
strategy back into a plain sid file. `INPUT` may be a strategy name (looked
up by invoking `eprover-ho` directly), a file path, or `-` for stdin.
Flags: `-1`/`--one-line` to print all arguments on one line; `-s`/`--no-sine`
to omit the `--sine` argument.

## ◆ `solverpy eval`, `solverpy loop`

Stubs reserved for a future non-YAML CLI form of `evaluate:`/`loop:`; not
yet implemented (they print an error and exit).

## ◆ Commands added by `solverpy-learn`

These subcommands only appear once `solverpy-learn` is installed.

### ▹ `solverpy tune TRAIN [TEST]`

Run the Optuna hyperparameter autotuner directly on an SVM-format training
(and optional testing) file, outside of a `loop:` experiment. Key flags:
`--phases` (which LightGBM parameter groups to tune, default `l:b:m:r`),
`--iters`, `--timeout`, `--min-leaves`/`--max-leaves`, `--posneg-weight`,
`--tmp`, `--model-out`, `--log-file`, and a set of `--init-*` flags for the
starting LightGBM parameters. Run `solverpy tune --help` for the full list.

### ▹ `solverpy compress INPUT` / `solverpy decompress INPUT`

Convert an SVM-Light training file to/from the chunked NPZ format used
internally for faster loading.

### ▹ `solverpy deconflict INPUT [OUTPUT]`

Remove training samples that appear as both positive and negative examples.
Default output: `deconflicted.in`.

### ▹ `solverpy filter INPUT [OUTPUT] --ratio R`

Subsample a training file to cap the positive/negative ratio: `--ratio r`
(with `r > 0`) caps negatives at `r` times the positive count; a negative
`r` caps positives at `|r|` times the negative count instead. Default
output: overwrite `INPUT`.
