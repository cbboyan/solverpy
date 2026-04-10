#!/usr/bin/env python3

if __name__ == "__main__":
   import json, os, argparse
   from grackle import jsondb

   parser = argparse.ArgumentParser(
      description='Join data from multiple grackle dbs.')
   parser.add_argument('input', nargs="+", 
      help="input grackle db json file(s)")
   parser.add_argument('output', action="store",
      help="output grackle db json file")
   parser.add_argument("-f", "--force", action="store_true",
      help="overwrite existing output file")
   parser.add_argument("-p", "--prefix", action="store_true",
      help="use directory names as prefixes (if possible)")
   args = parser.parse_args()
   
   if (not args.force) and os.path.isfile(args.output):
      print("Error: Output file exists.  Use -f to override.")
   else:
      print("loading..")
      prefs = None
      if args.prefix:
         prefs = [os.path.dirname(x)+"/" for x in args.input]
         if len(args.input) != len(set(prefs)):
            prefs = None
      joint = jsondb.join(args.input, prefs)
      print("saving..")
      json.dump(joint, open(args.output,"w"), indent=3, sort_keys=True)
      print("done.")

