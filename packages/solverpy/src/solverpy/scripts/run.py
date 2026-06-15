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

   trains = yaml_data.setdefault("trains", {})
   for key in ("benchmarks", "strategies", "bidfile", "sidfile"):
      if key in yaml_data and key not in trains:
         trains[key] = yaml_data.pop(key)
   solver_fn(yaml_data)
   setups.experiment(yaml_data)
   setups.evaluation(yaml_data)
   setups.launch(yaml_data)


def _run_loop(loop_type, yaml_data):
   sid = yaml_data.get("strategy")
   if not sid:
      print("error: 'loop' requires a 'strategy' key.", file=sys.stderr)
      sys.exit(1)

   common = yaml_data.get("common", {})
   train_dict = yaml_data.get("train", {})
   devel_dict = yaml_data.get("devel", None)
   tune = yaml_data.get("tune", None)

   try:
      from solverpy_learn import setups
   except ImportError:
      print("error: 'loop' requires the solverpy-learn package.", file=sys.stderr)
      sys.exit(1)

   setup = setups.Setup(**common)
   setup["trains"] = setups.Evalset(strategies=[sid], refs=[sid], **train_dict)
   if devel_dict:
      setup["devels"] = setups.Evalset(strategies=[sid], refs=[sid], **devel_dict)
   setups.experiment(setup)

   if loop_type == "enigma":
      setups.eprover(setup, training=True)
      if devel_dict:
         setups.eprover(setup, training=True, key="devels")
      setups.evaluation(setup)
      setups.enigma(setup, tunesel=tune)
   elif loop_type == "cvc5ml":
      setups.cvc5(setup, training=True)
      if devel_dict:
         setups.cvc5(setup, training=True, key="devels")
      setups.evaluation(setup)
      setups.cvc5ml(setup, tuneargs=tune)

   setups.launch(setup)


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
