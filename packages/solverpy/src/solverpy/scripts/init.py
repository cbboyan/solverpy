from pathlib import Path
from importlib.resources import files


def _data_strats():
   return files("solverpy") / "data" / "strats"


def _data_setups():
   return files("solverpy") / "data" / "setups"


def _copy(src, dest, prefix=""):
   for f in src.iterdir():
      if not f.is_file():
         continue
      name = f.name
      if prefix and name.startswith(prefix):
         name = name[len(prefix):]
      target = dest / name
      target.write_bytes(f.read_bytes())


def _solvers():
   return sorted(d.name for d in _data_strats().iterdir() if d.is_dir())


def main(args):
   solver = args.solver
   strats_dir = Path("solverpy_db") / "strats"
   strats_dir.mkdir(parents=True, exist_ok=True)

   data = _data_strats()

   if solver:
      _copy(data / solver, strats_dir, prefix=f"{solver}-")
      setup_src = _data_setups() / f"eval-{solver}.yml"
      if setup_src.is_file():
         dest = Path(f"eval-{solver}.yml")
         dest.write_bytes(setup_src.read_bytes())
         print(f"Created {dest}")
   else:
      for solver_dir in data.iterdir():
         if solver_dir.is_dir():
            _copy(solver_dir, strats_dir)

   print(f"Initialized {strats_dir}")


def register(subparsers):
   solvers = _solvers()
   p = subparsers.add_parser(
      "init",
      help="Initialize a new solverpy project.",
      description="Create solverpy_db/strats/ in the current directory and populate it with bundled strategies.",
   )
   p.add_argument("solver", nargs="?", choices=solvers, metavar="SOLVER",
                  help=f"Solver to initialize for. Available: {', '.join(solvers)}. Omit to copy all.")
   p.set_defaults(func=main)
