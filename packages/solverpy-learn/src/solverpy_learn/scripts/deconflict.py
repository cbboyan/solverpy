def register(subparsers):
   p = subparsers.add_parser(
      "deconflict",
      help="Remove conflicting positive/negative training samples.",
   )
   p.add_argument("input", metavar="input.in",
                  help="Input training file (plain or compressed).")
   p.add_argument("output", metavar="output.in", nargs="?",
                  default="deconflicted.in",
                  help="Output file (default: deconflicted.in).")
   p.add_argument("-v", "--verbose", action="store_true",
                  help="Show more details.")
   p.set_defaults(func=main)


def main(args):
   import logging
   level = logging.DEBUG if args.verbose else logging.INFO
   logging.basicConfig(level=level, format="%(message)s")
   from solverpy_learn.builder import svm
   (xs, ys) = svm.load(args.input)
   (xs0, ys0) = svm.deconflict(xs, ys)
   svm.save(xs0, ys0, args.output)
