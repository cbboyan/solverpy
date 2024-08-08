#!/usr/bin/env python

import subprocess

# commits with the following types are skiped in the change log
SKIP_TYPE = ["chore"]

# skip all commits with one of these keywords in the change log
SKIP_MSG = ["README", "CHANGELOG", "changelog"]

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

def gitversion(ver):
   tag = f"v{'.'.join(map(str,ver))}"
   return tag

def gittags(commits):
   cur = [0, 0, 0]  # [MAJOR, MINOR, PATCH]
   tags = []
   for (hsh, ver, typ, msg) in commits:
      if ver:
         cur = ver
         continue # this commit already has a version tag
      if typ: # but not ver
         if typ.endswith("!!!"):
            cur = [cur[0]+1, 0, 0] # increase MAJOR
         elif typ.endswith("!!"):
            cur = [cur[0], cur[1]+1, 0] # increase MINOR
         elif typ.endswith("!"):
            cur = [cur[0], cur[1], cur[2]+1] # increase PATCH
         else: 
            continue # this commit needs no version tag
         tags.append((hsh, cur))
   return tags

def gitchanges(commits):
   changes = []
   cur = []
   for (hsh, ver, typ, msg) in commits:
      if (typ in SKIP_TYPE) or any((skip in msg) for skip in SKIP_MSG):
         continue # skip this commit in the change log
      cur.append((hsh, typ, msg))
      if ver:
         cur.reverse()
         changes.append((gitversion(ver), cur))
         cur = []
   if cur:
      cur.reverse()
      changes.append(("Unreleased changes", cur))
   changes.reverse()
   return changes

def gitdate(hsh):
   cmd = f"git log -1 --pretty=format:'%ad' --date=short {hsh}"
   return subprocess.check_output(cmd, shell=True).decode()

def changelog(commits):
   changes = gitchanges(commits)
   lines = []
   for (ver, coms) in changes:
      date = gitdate(coms[0][0])
      lines.append(f"## {ver} ({date})")
      lines.append("")
      for (hsh, typ, msg) in coms:
         typ = f"{typ}: " if typ else ""
         url = f"https://github.com/cbboyan/solverpy/commit/{hsh}"
         lines.append(f"* {typ}{msg} [View]({url})")
      lines.append("")
   return "\n".join(lines)
   
#commits = gitlog()
#print(changelog(commits))

if __name__ == "__main__":
   commits = gitlog()
   tags = gittags(commits)
   if tags:
      print("Run the following commands (and then `git push --tags`):")
   else:
      print("Version tags are up-to-date.")
   for (hsh, ver) in tags:
      tag = gitversion(ver)
      cmd = f"git tag -a {tag} {hsh} -m 'Version {tag}'"
      print(cmd)

