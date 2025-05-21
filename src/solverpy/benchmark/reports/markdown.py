from typing import Any, Callable, TYPE_CHECKING
import yaml as pyyaml
import logging

from . import data

if TYPE_CHECKING:
   from ...tools.typing import Report, SolverJob, Result
   from ...solver.solverpy import SolverPy

logger = logging.getLogger(__name__)

__all__ = ["newline", "text", "heading", "table"]


def widths(
   rows: list[list[str]],
   header: list[str] | None = None,
) -> list[int]:
   rows = (rows + [header]) if header else rows
   ncols = len(rows[0])
   width = [0] * ncols
   for i in range(ncols):
      width[i] = max(len(str(row[i])) for row in rows)
   return width


def join(
   row: list[str],
   width: list[int],
   sep: str = "|",
   padding: str = " ",
) -> str:
   psep = f"{padding}{sep}{padding}"
   line = psep.join(f"{val:{width[i]}}" for (i, val) in enumerate(row))
   return f"{sep}{padding}{line}{padding}{sep}"


def newline() -> "Report":
   return [""]


def heading(title: str, level: int = 1) -> "Report":
   level0 = "#" * level
   return [f"{level0} {title}", ""]


def text(txt: str) -> "Report":
   return [txt]


def yaml(obj: Any) -> "Report":
   if type(obj) is str:
      txt = obj
   else:
      txt = pyyaml.dump(obj, default_flow_style=False)
   lines = []
   lines.append("```yaml")
   lines.extend(txt.strip().split("\n"))
   lines.append("```")
   return lines


def table(
   header: list[str],
   rows: list[list[Any]],
   key: Callable[[list[Any]], Any] | None = None,
) -> "Report":
   logger.debug(
      f"making table with {len(rows)} rows and {len(rows[0])} columns")
   width = widths(rows, header=header)
   lines = []
   if header:
      lines.append(join(header, width))
   delims = ["-" * (w + 2) for w in width]
   lines.append(join(delims, width, padding=""))
   if key is not None:
      rows = sorted(rows, reverse=True, key=key)
   for row in rows:
      lines.append(join(row, width))
   return lines


def summary(
   results: dict["SolverJob", dict[str, Any]],
   nicks: dict["SolverJob", str],
   ref: "SolverJob | None" = None,
) -> "Report":
   logger.debug(f"creating summary for {len(results)} results")
   if ref is None:
      header = ["name", "solved", "PAR2", "unsolved", "timeouts", "errors"]
      refsolved = None
      refpar2 = None
   else:
      header = [
         "name", "solved", "ref+", "ref-", "PAR2", "PAR2+", "unsolved",
         "timeouts", "errors"
      ]
      refsolved = frozenset(p for (p, r) in results[ref].items()
                            if ref[0].solved(r))
      refpar2 = sum(data.par2score(ref[0], r) for r in results[ref].values())

   rows: list[list[Any]] = []
   for ((solver, bid, sid), res) in results.items():
      row: list[Any] = [nicks[(solver, bid, sid)]]
      row.extend(data.summary(solver, bid, sid, res, refsolved, refpar2))
      rows.append(row)
   lines = table(header, rows, key=lambda x: x[1:])
   logger.debug(f"summary created")
   return lines


def statuses(
   results: dict["SolverJob", dict[str, Any]],
   nicks: dict["SolverJob", str],
) -> "Report":
   logger.debug(f"creating statuses for {len(results)} results")

   def safestat(r: "Result | None") -> str:
      if r is None:
         return "NONE"
      elif "status" in r:
         return r["status"]
      else:
         return "MISSING"

   def count(status: str, res: dict[str, "Result | None"]) -> int:
      return sum(1 for r in res.values() if safestat(r) == status)

   some: "SolverPy" = list(results.keys())[0][0]

   def rank(status: str) -> tuple[int, str]:
      if status in some.success:
         return (0, status)
      elif status in some.timeouts:
         return (2, status)
      else:
         return (1, status)

   allstats = frozenset(
      safestat(r) for res in results.values() for r in res.values())
   allstats = sorted(allstats, key=rank)
   header = ["name"] + allstats
   rows = []
   for ((solver, bid, sid), res) in results.items():
      row = [nicks[(solver, bid, sid)]]
      row += [count(status, res) for status in allstats]
      rows.append(row)
   lines = table(header, rows, key=lambda x: x[1:])
   logger.debug(f"statuses created")
   return lines


def collect(
   report: "Report",
   acc: list[str] | None = None,
) -> list[str]:
   if acc is None: acc = []
   for line in report:
      if isinstance(line, str):
         acc.append(line)
      else:
         assert (type(line) is list) or (type(line) is tuple)
         collect(line, acc)
   return acc


def dump(report: "Report", prefix: str = "") -> str:
   if not report:
      return ""
   return f"{prefix}" + f"\n{prefix}".join(collect(report))

