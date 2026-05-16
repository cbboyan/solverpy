from typing import Any, TYPE_CHECKING

from .path import bids
from .reports import markdown
from ..tools import reporter

if TYPE_CHECKING:
   from ..tools.typing import SolverJob

def legend(
   jobs: list["SolverJob"],
   ref: "SolverJob | None" = None,
   sidnames: bool = False,
) -> tuple[dict["SolverJob", str], str, str]:
   nicks = {}
   if sidnames:
      header = ["#", "strategy", "benchmark", "solver", "problems"]
   else:
      header = ["name", "strategy", "benchmark", "solver", "problems"]
   rows = []
   width = 0
   for (n, job) in enumerate(jobs):
      (solver, bid, sid) = job
      if sidnames:
         nick = f"s{n+1}"
         if job == ref: nick = f"s{n+1}*"
      else:
         nick = "ref" if job == ref else f"{n}/{len(jobs)-1}"
      nicks[job] = nick
      width = max(width, len(nick))
      rows.append([nick, sid, bid, solver.name, len(bids.problems(bid))])

   totaldesc = "total"
   width = max(width, len(totaldesc)) + 1
   totaldesc = f"{totaldesc:{width}}"
   nicks = {x: f"{y:{width}}" for (x, y) in nicks.items()}

   report = markdown.newline()
   report += markdown.heading("Legend", level=3)
   report += markdown.table(header, rows)
   report += markdown.newline()
   reporter.add(report)
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

   reporter.add(report)
   return markdown.dump(report, prefix="> ")

