def register(subparsers):
   p = subparsers.add_parser(
      "compress",
      help="Compress SVM training file to chunked NPZ format.",
   )
   p.add_argument("input", metavar="train.in",
                  help="Training file in SVM-Light format.")
   p.set_defaults(func=main)


def main(args):
   import logging
   logging.basicConfig(level=logging.INFO, format="%(message)s")
   from solverpy_learn.builder import svm
   svm.compress(args.input)
