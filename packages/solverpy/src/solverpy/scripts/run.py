import sys
from pathlib import Path
import yaml


def main(args):
   from solverpy.tools import log
   log.init(Path(args.file).name)

   with open(args.file) as f:
      setup = yaml.safe_load(f)

   evaluate = setup.pop("evaluate", None)
   if not evaluate:
      print("error: YAML file must contain 'evaluate: <solver>'.", file=sys.stderr)
      sys.exit(1)

   from solverpy import setups
   solver_fn = getattr(setups, evaluate, None)
   if solver_fn is None:
      print(f"error: unknown solver '{evaluate}'.", file=sys.stderr)
      sys.exit(1)

   solver_fn(setup)
   setups.evaluation(setup)
   setups.launch(setup)


def register(subparsers):
   p = subparsers.add_parser(
      "run",
      help="Run an evaluation from a YAML setup file.",
      description="Load a YAML setup file and run benchmark evaluation.",
   )
   p.add_argument("file", metavar="FILE", help="Path to YAML setup file.")
   p.set_defaults(func=main)
