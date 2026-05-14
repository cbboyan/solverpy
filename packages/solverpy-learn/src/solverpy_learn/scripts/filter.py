def register(subparsers):
   p = subparsers.add_parser(
      "filter",
      help="Filter positive/negative training samples by ratio.",
   )
   p.add_argument("input", metavar="input.in",
                  help="Input training file (plain or compressed).")
   p.add_argument("output", metavar="output.in", nargs="?", default=None,
                  help="Output file (default: overwrite input).")
   p.add_argument("--ratio", type=float, metavar="r", required=True,
                  help="Max neg/pos ratio (>0) or max pos/neg ratio as negative value (<0).")
   p.add_argument("--seed", type=int, metavar="s", default=0,
                  help="Random seed for sampling (default: 0).")
   p.add_argument("-v", "--verbose", action="store_true",
                  help="Show debug details.")
   p.set_defaults(func=main)


def main(args):
   import random
   import logging
   import numpy
   level = logging.DEBUG if args.verbose else logging.INFO
   logging.basicConfig(level=level, format="%(message)s")
   from solverpy_learn.builder import svm

   (xs, ys) = svm.load(args.input)

   pos_idx = numpy.where(ys == 1)[0]
   neg_idx = numpy.where(ys == 0)[0]

   random.seed(args.seed)
   if args.ratio > 0 and len(pos_idx) * args.ratio < len(neg_idx):
      neg_idx = numpy.array(random.sample(list(neg_idx), int(len(pos_idx) * args.ratio)))
   elif args.ratio < 0 and len(neg_idx) * (-args.ratio) < len(pos_idx):
      pos_idx = numpy.array(random.sample(list(pos_idx), int(len(neg_idx) * (-args.ratio))))

   keep = numpy.sort(numpy.concatenate([pos_idx, neg_idx]))
   svm.save(xs[keep], ys[keep], args.output or args.input)
