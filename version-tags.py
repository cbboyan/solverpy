#!/usr/bin/env python3

import subprocess

def gitlog():
   commits = []
   logs = subprocess.check_output("git log --oneline --decorate --decorate-refs=tags", shell=True)
   logs = logs.decode().strip().split("\n")
   for commit in logs:
      parts = commit.split(" ")
      hsh = parts[0]
      i = 1
      tag = None
      if parts[1] == "(tag:":
         tag = parts[2].rstrip(")")
         i = 3
      ver = None
      if tag and tag.startswith("v"):
         ver = [int(x) for x in tag[1:].split(".")]
      typ = None
      if parts[i].endswith(":"):
         typ = parts[i].rstrip(":")
         i += 1
      msg = " ".join(parts[i:])
      commits.append((hsh, ver, typ, msg))
   commits.reverse()
   return commits

def gittags():
   commits = gitlog()
   cur = [0, 0, 0]  # [MAJOR, MINOR, PATCH]
   for (hsh, ver, typ, msg) in commits:
      if ver:
         cur = ver
         continue # this commit already has a version tag
      if typ: # but not ver
         if typ.endswith("!"):
            cur = [cur[0]+1, 0, 0] # increase MAJOR
         elif typ.startswith("feat"):
            cur = [cur[0], cur[1]+1, 0] # increase MINOR
         elif typ.startswith("fix"):
            cur[2] += 1 # increase PATCH
         else: 
            continue # this commit needs no version tag
         tag = f"v{'.'.join(map(str,cur))}"
         cmd = f"git tag -a {tag} {hsh} -m 'Version {tag}'"
         print(cmd)

if __name__ == "__main__":
   gittags()

