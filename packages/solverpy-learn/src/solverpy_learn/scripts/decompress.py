def register(subparsers):
   p = subparsers.add_parser(
      "decompress",
      help="Decompress chunked NPZ training file back to SVM-Light format.",
   )
   p.add_argument("input", metavar="train.in",
                  help="Compressed training file (chunked NPZ).")
   p.set_defaults(func=main)


def main(args):
   import logging
   logging.basicConfig(level=logging.INFO, format="%(message)s")
   from solverpy_learn.builder import svm
   svm.decompress(args.input, keep=True)
