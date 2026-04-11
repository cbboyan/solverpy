#!/usr/bin/env python3

from grackle import jsondb

if __name__ == "__main__":
   import argparse
   
   parser = argparse.ArgumentParser(
      description='List performance of strategies in grackle db.')
   parser.add_argument('dbfile', nargs="?", default="db-trains-cache.json", 
      help="grackle db json filename (default: db-trains.cache.json)")
   parser.add_argument("-t", "--table", nargs="?", const="translate.txt", default=None,
      help="specify a translation table (default: translate.txt)")
   parser.add_argument("-r", "--restrict", default=None,
      help="restrict the set of problems to the problems from file")
   parser.add_argument("-s", "--scores", action="store_true", default=False,
      help="show strategy score"),
   parser.add_argument("-l", "--limit", type=float, 
      help="set time limit for solved problems"),
   group = parser.add_mutually_exclusive_group()
   group.add_argument("--new", action="store_true", 
      help="consider only newly genereted strategies (requires translation table)")
   group.add_argument("--old", action="store_true", 
      help="consider only initial strategies (requires translation table)")
   args = parser.parse_args()
   
   fm = True if args.old else (False if args.new else None)
   results = jsondb.load(args.dbfile, args.table, filter_mode=fm, f_restrict=args.restrict)
   cnts = jsondb.counts(results, limit=args.limit)
   if args.scores:
      scores = jsondb.scores(results, results)
      cnts = {c:(scores[c],cnts[c]) for c in cnts}
   jsondb.perf(cnts)
   
   #sims = jsondb.similars(results, results)
   #def sims0(s, t):
   #   return sims[s][t]
   #for s in sims:
   #   ts = sorted(sims[s], key=lambda t: sims0(s,t), reverse=True)[:3]
   #   print(s, "::", " ".join(f"{sims[s][t]}#{t}" for t in ts))

