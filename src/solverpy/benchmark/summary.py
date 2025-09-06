from typing import Any, TYPE_CHECKING

from .path import bids
from .reports import markdown

if TYPE_CHECKING:
   from ..tools.typing import SolverJob

def legend(
   jobs: list["SolverJob"],
   ref: "SolverJob | None" = None,
   sidnames: bool = False,
) -> tuple[dict["SolverJob", str], str, str]:
   nicks = {}
   if sidnames:
      header = ["name", "solver", "benchmark", "problems"]
   else:
      header = ["name", "solver", "benchmark", "strategy", "problems"]
   rows = []
   width = 0
   for (n, job) in enumerate(jobs):
      (solver, bid, sid) = job
      if sidnames:
         nick = sid
         if job == ref: nick = f"* {nick}"
      else:
         nick = "ref" if job == ref else f"{n}/{len(jobs)-1}"
      nicks[job] = nick
      width = max(width, len(nick))
      if sidnames:
         rows.append([nick, solver.name, bid, len(bids.problems(bid))])
      else:
         rows.append([nick, solver.name, bid, sid, len(bids.problems(bid))])

   totaldesc = "total"
   totaldesc = f"{totaldesc:{width}}"
   nicks = {x: f"{y:{width}}" for (x, y) in nicks.items()}

   report = markdown.newline()
   report += markdown.heading("Legend", level=3)
   report += markdown.table(header, rows)
   report += markdown.newline()
   report0 = markdown.dump(report, prefix="> ")

   return (nicks, totaldesc, report0)


def summarize(
   allres: dict["SolverJob", Any],
   nicks: dict["SolverJob", str],
   ref: "SolverJob | None" = None,
) -> str:
   report = markdown.newline()
   report += markdown.heading("Summary", level=3)
   report += markdown.summary(allres, nicks, ref=ref)

   report += markdown.newline()
   report += markdown.heading("Statuses", level=3)
   report += markdown.statuses(allres, nicks)
   report += markdown.newline()

   return markdown.dump(report, prefix="> ")

