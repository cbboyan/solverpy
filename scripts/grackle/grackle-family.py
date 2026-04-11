#!/usr/bin/env python3

from os import path
import json

def read(conf, cdir, cache={}):
   if conf in cache: return cache[conf]
   lst = open(path.join(cdir, conf)).read().strip().split()
   ps = {}
   while lst:
      key = lst.pop(0).lstrip("-").strip()
      val = lst.pop(0).strip()
      ps[key] = val
   cache[conf] = ps
   return ps

def diff(dict1, dict2):
   defs = {x:"*" for x in dict1.keys() | dict2.keys()}
   dict1 = dict(defs, **dict1)
   dict2 = dict(defs, **dict2)
   df = {x:(dict1[x], dict2[x]) for x in defs if dict1[x] != dict2[x]}
   return df

def trace(conf, family, cdir, diffs):
   roots = [conf]
   while conf in family:
      conf = family[conf]
      roots.append(conf)
   roots.reverse()

   init = roots[0]
   prev = roots[1]
   if diffs:
      base = read(prev, cdir)
      first = dict(base)
   print(f"# INIT: {prev} = {init}")
   
   for conf in roots[2:]:
      print(f"# EVOLVE: {prev} --> {conf}")
      if diffs:
         now = read(conf, cdir)
         df = diff(base, now)
         print_diff(df)
         base = now
      prev = conf
   
   if diffs:
      print(f"# FINAL DIFFERENCE:")
      df = diff(first, base)
      print_diff(df)

def print_family(family):
   print("\n".join(f"{x}: {y}" for (x,y) in sorted(family.items())))
   
def print_diff(df):
   print("\n".join("> %30s: %5s -> %5s" % (x, df[x][0], df[x][1]) for x in sorted(df)))
   print()

if __name__ == "__main__":
   import argparse

   parser = argparse.ArgumentParser(
      description='Display all ancestor roots of a given configuration.')
   parser.add_argument("-f", "--family", default="grackle.flee-family.json", metavar="JSON",
      help="specify a family tree (default: grackle.flee-family.json)")
   parser.add_argument("-c", "--confs", default="confs", metavar="DIR",
         help="specify the directory with configurations (default: ./confs)")
   parser.add_argument("-d", "--diffs", action="store_true",
      help="show configuration differences (requires configuration definitions -c)")
   group = parser.add_mutually_exclusive_group()
   group.add_argument("-l", "--list", action="store_true",
      help="list family members (configurations)")
   group.add_argument('conf', nargs="?", default=None,
      help="show the heritage line of this configuration")
   args = parser.parse_args()

   family = json.load(open(args.family))
   if args.list:
      print_family(family)
   else:
      conf = args.conf
      if conf not in family:
         print("Error: Unknow configuration: %s" % conf)
      else:
         trace(conf, family, args.confs, args.diffs)


