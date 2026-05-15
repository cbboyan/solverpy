import sys
from pathlib import Path
from importlib.resources import files


def _data_strats():
   return files("solverpy") / "data" / "strats"


def _copy(src, dest, prefix=""):
   for f in src.iterdir():
      if not f.is_file():
         continue
      name = f.name
      if prefix and name.startswith(prefix):
         name = name[len(prefix):]
      target = dest / name
      target.write_bytes(f.read_bytes())


def main(args):
   solver = args.solver
   strats_dir = Path("solverpy_db") / "strats"
   strats_dir.mkdir(parents=True, exist_ok=True)

   data = _data_strats()

   if solver:
      src = data / solver
      if not src.is_dir():
         solvers = [d.name for d in data.iterdir() if d.is_dir()]
         print(f"error: unknown solver '{solver}'. Available: {', '.join(sorted(solvers))}",
               file=sys.stderr)
         sys.exit(1)
      _copy(src, strats_dir, prefix=f"{solver}-")
   else:
      for solver_dir in data.iterdir():
         if solver_dir.is_dir():
            _copy(solver_dir, strats_dir)

   print(f"Initialized {strats_dir}")


def register(subparsers):
   p = subparsers.add_parser(
      "init",
      help="Initialize a new solverpy project.",
      description="Create solverpy_db/strats/ in the current directory and populate it with bundled strategies.",
   )
   p.add_argument("solver", nargs="?", metavar="SOLVER",
                  help="Solver to initialize for (e.g. eprover). Omit to copy all solvers.")
   p.set_defaults(func=main)
