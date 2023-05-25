import logging

from . import data

logger = logging.getLogger(__name__)

def widths(rows, header=None):
   rows = (rows + [header]) if header else rows
   ncols = len(rows[0])
   width = [0] * ncols
   for i in range(ncols):
      width[i] = max(len(str(row[i])) for row in rows)
   return width

def join(row, width, sep="|", padding=" "):
   psep = f"{padding}{sep}{padding}"
   line = psep.join(f"{val:{width[i]}}" for (i,val) in enumerate(row))
   return f"{sep}{padding}{line}{padding}{sep}"


def newline():
   return [""]

def heading(title, level=1):
   level = "#" * level
   return [ f"{level} {title}", "" ]

def table(header, rows, key=None):
   logger.debug(f"making table with {len(rows)} rows and {len(header)} columns")
   width = widths(rows, header=header)
   lines = []
   lines.append(join(header, width))
   delims = [ "-"*(w+2) for w in width ]
   lines.append(join(delims, width, padding=""))
   if key is not None:
      rows = sorted(rows, reverse=True, key=key)
   for row in rows:
      lines.append(join(row, width))
   return lines




def summary(results, nicks, ref=None):
   logger.debug(f"creating summary for {len(results)} results")
   if ref is None:
      header = ["name", "solved", "PAR2", "unsolved", "timeouts", "errors"]
      refsolved = None
      refpar2 = None
   else:
      header = ["name", "solved", "ref+", "ref-", "PAR2", "PAR2+", "unsolved", "timeouts", "errors"]
      refsolved = frozenset(p for (p,r) in results[ref].items() if ref[0].solved(r))
      refpar2 = sum(data.par2score(ref[0], r) for r in results[ref].values())

   rows = []
   for ((solver,bid,sid),res) in results.items():
      row = [ nicks[(solver,bid,sid)] ]
      row.extend(data.summary(solver,bid,sid,res,refsolved,refpar2))
      rows.append(row)
   lines = table(header, rows, key=lambda x: x[1:])
   logger.debug(f"summary created")
   return lines

def statuses(results, nicks):
   logger.debug(f"creating statuses for {len(results)} results")
   
   def count(status, res):
      return sum(1 for r in res.values() if "status" in r and r["status"]==status)

   some = list(results.keys())[0][0]
   def rank(status):
      if status in some.success: 
         return (0, status)
      elif status in some.timeouts: 
         return (2, status)
      else: 
         return (1, status)

   allstats = frozenset(r["status"] for res in results.values() for r in res.values() if "status" in r)
   allstats = sorted(allstats, key=rank)
   header = ["name"] + allstats
   rows = []
   for ((solver,bid,sid),res) in results.items():
      row = [ nicks[(solver,bid,sid)] ]
      row += [ count(status, res) for status in allstats ] 
      rows.append(row)
   lines = table(header, rows, key=lambda x: x[1:])
   logger.debug(f"statuses created")
   return lines

def dump(report, prefix=""):
   return f"{prefix}" + f"\n{prefix}".join(report) 

