import argparse
import sys


def _not_implemented(name):
   print(f"error: 'solverpy {name}' is not yet implemented.", file=sys.stderr)
   sys.exit(1)


def _add_stub(subparsers, name, help_text, args_help=None):
   p = subparsers.add_parser(name, help=help_text)
   if args_help:
      for (metavar, h) in args_help:
         p.add_argument(metavar.lower().replace("-", "_"), metavar=metavar,
                        nargs="?", help=h)
   p.set_defaults(func=lambda _: _not_implemented(name))


def main():
   parser = argparse.ArgumentParser(
      prog="solverpy",
      description="Command-line interface for solverpy.",
   )
   subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

   from solverpy.scripts import esid2strat, init
   esid2strat.register(subparsers)
   init.register(subparsers)
   _add_stub(subparsers, "eval",
             "Run benchmark evaluation.",
             [("sid", "Strategy id."), ("bid", "Benchmark id.")])
   _add_stub(subparsers, "loop",
             "Run the iterative eval/build loop.",
             [("bid-train", "Training benchmark id."), ("bid-devel", "Development benchmark id.")])
   _add_stub(subparsers, "launch",
             "Launch a setup from a YAML file.",
             [("setup", "Path to setup YAML file.")])

   try:
      from solverpy_learn.scripts import autotune, compress, decompress, deconflict
      from solverpy_learn.scripts import filter as filter_cmd
      autotune.register(subparsers)
      compress.register(subparsers)
      decompress.register(subparsers)
      deconflict.register(subparsers)
      filter_cmd.register(subparsers)
   except ImportError:
      pass

   if len(sys.argv) == 1:
      parser.print_help()
      sys.exit(0)

   args = parser.parse_args()
   if not hasattr(args, 'func'):
      parser.print_help()
      sys.exit(1)
   args.func(args)
