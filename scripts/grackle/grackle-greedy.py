#!/usr/bin/env python3

from grackle import jsondb


if __name__ == "__main__":
   import argparse

   parser = argparse.ArgumentParser(
      description='Construct a greedy cover of strategies in grackle db.')
   parser.add_argument("-n", type=int, 
      help="limit the size of the greedy cover")
   parser.add_argument("-i", "--iterate", nargs="?", type=int, default=None, const=True,
      help="iterated greedy cover construction")
   parser.add_argument("-b", "--bests", type=int, default=1,
      help="how many best strategies not to use for an iterated greedy cover"),
   parser.add_argument("-t", "--table", nargs="?", const="translate.txt", default=None,
      help="specify a translation table (default: translate.txt)")
   parser.add_argument("-r", "--restrict", default=None,
      help="restrict the set of problems to the problems from file")
   parser.add_argument('dbfile', nargs="?", default="db-trains-cache.json", 
      help="grackle db json filename (default: db-trains-cache.json)")
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
   results = jsondb.solved(results, limit=args.limit)

   if args.iterate:
      done = set()
      backup = {x:set(y) for (x,y) in results.items()}
      i = 0
      while results and ((args.iterate is True) or (i < args.iterate)):
         print("### GREEDY COVER #%s" % i)
         cover = jsondb.greedy(results, max_n=args.n)
         print()
         #done.add(cover[0])
         done.update(cover[:args.bests])
         results = {x:set(y) for (x,y) in backup.items() if x not in done}
         i += 1
   else:
      jsondb.greedy(results, max_n=args.n)

