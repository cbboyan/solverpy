import sys
from pathlib import Path
import yaml

LOOP_TYPES = ["enigma", "cvc5ml"]


def _run_evaluate(yaml_data):
   evaluate = yaml_data.pop("evaluate", None)
   if not evaluate:
      print("error: YAML file must contain 'evaluate: <solver>' or 'loop: <type>'.",
            file=sys.stderr)
      sys.exit(1)

   from solverpy import setups
   solver_fn = getattr(setups, evaluate, None)
   if solver_fn is None:
      print(f"error: unknown solver '{evaluate}'.", file=sys.stderr)
      sys.exit(1)

   setups.experiment(yaml_data)
   solver_fn(yaml_data)
   setups.evaluation(yaml_data)
   setups.launch(yaml_data)


def _run_loop(loop_type, yaml_data):
   sid = yaml_data.pop("strategy", None)
   if not sid:
      print("error: 'loop' requires a 'strategy' key.", file=sys.stderr)
      sys.exit(1)

   common = yaml_data.setdefault("common", {})
   common.setdefault("strategies", [sid])
   common.setdefault("refs", [sid])
   tune = yaml_data.pop("tune", None)

   try:
      from solverpy_learn import setups
   except ImportError:
      print("error: 'loop' requires the solverpy-learn package.", file=sys.stderr)
      sys.exit(1)

   setups.experiment(yaml_data)

   if loop_type == "enigma":
      setups.eprover(yaml_data)
      setups.evaluation(yaml_data)
      setups.enigma(yaml_data, tunesel=tune)
   elif loop_type == "cvc5ml":
      setups.cvc5(yaml_data)
      setups.evaluation(yaml_data)
      setups.cvc5ml(yaml_data, tuneargs=tune)

   setups.launch(yaml_data)


def main(args):
   from solverpy.report import log
   log.init(Path(args.file).name)

   with open(args.file) as f:
      yaml_data = yaml.safe_load(f)

   loop_type = yaml_data.pop("loop", None)
   if loop_type:
      if loop_type not in LOOP_TYPES:
         print(f"error: unknown loop type '{loop_type}'. Must be one of: {', '.join(LOOP_TYPES)}.",
               file=sys.stderr)
         sys.exit(1)
      _run_loop(loop_type, yaml_data)
   else:
      _run_evaluate(yaml_data)


def register(subparsers):
   p = subparsers.add_parser(
      "run",
      help="Run an evaluation from a YAML setup file.",
      description="Load a YAML setup file and run benchmark evaluation.",
   )
   p.add_argument("file", metavar="FILE", help="Path to YAML setup file.")
   p.set_defaults(func=main)
