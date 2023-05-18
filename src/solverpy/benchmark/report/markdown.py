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



def heading(title, level=1):
   level = "#" * level
   return [ f"{level} {title}", "" ]

def table(header, rows, key=None):
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




def summary(results, nicks, pref=">", ref=None):
   logger.debug(f"creating summary for {len(results)} results")
   if ref is None:
      header = ["solver", "solved", "unsolved", "timeouts", "errors"]
   else:
      header = ["solver", "solved", "ref+", "ref-", "unsolved", "timeouts", "errors"]
      refsolved = frozenset(p for (p,r) in results[ref].items() if ref[0].solved(r))

   #header = []
   #for key in results:
   #   header.append(nicks[key])
   rows = []
   for ((solver,bid,sid),res) in results.items():
      row = [ nicks[(solver,bid,sid)] ]
      row.extend(data.summary(solver,bid,sid,res,refsolved))
      rows.append(row)
   lines = table(header, rows, key=lambda x: x[1])
   logger.debug(f"summary created")
   return lines

def dump(report, prefix=""):
   return f"{prefix}" + f"\n{prefix}".join(report) 


   
