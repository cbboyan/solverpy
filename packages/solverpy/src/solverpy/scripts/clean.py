import sys
import shutil
from pathlib import Path


def main(args):
   db = Path("solverpy_db")
   if not db.is_dir():
      print("error: no solverpy_db directory found in current directory.", file=sys.stderr)
      sys.exit(1)

   targets = [d for d in db.iterdir() if d.is_dir() and d.name != "strats"]
   if not targets:
      print("Nothing to clean.")
      return

   if not args.yes:
      names = ", ".join(sorted(d.name for d in targets))
      answer = input(f"Delete solverpy_db/{{{names}}}? [y/N] ")
      if answer.strip().lower() != "y":
         print("Aborted.")
         sys.exit(0)

   for d in targets:
      shutil.rmtree(d)
      print(f"Deleted {d}")


def register(subparsers):
   p = subparsers.add_parser(
      "clean",
      help="Delete all solverpy_db subdirectories except strats/.",
      description="Delete all subdirectories of solverpy_db/ in the current directory, except strats/.",
   )
   p.add_argument("-y", "--yes", action="store_true",
                  help="Skip confirmation prompt.")
   p.set_defaults(func=main)
