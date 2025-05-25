from typing import Any, TYPE_CHECKING
import random
import logging

from .path import bids
from ..tools import log
from ..task.solvertask import SolverTask
from ..task.bar import SolvingBar, RunningBar
from ..task import launcher
from .reports import markdown
from .db.providers.solved import Solved
from .setups.setup import Setup

if TYPE_CHECKING:
   from .db.db import DB
   from ..solver.solverpy import SolverPy
   from ..tools.typing import Result, SolverJob

logger = logging.getLogger(__name__)


def init(setup: Setup | None = None):
   log.init()
   if setup:
      report = []
      report.extend(markdown.heading("Experiments", level=2))
      report.extend(markdown.heading("Setup", level=3))
      report.extend(markdown.yaml(setup))
      report.extend(markdown.newline())
      report = markdown.dump(report, prefix="> ")
   else:
      report = ""
   logger.info(f"Experiments running.\n{report}")


def jobname(solver: Any, bid: str, sid: str) -> str:
   return f"{solver}:{sid} @ {bid}"


def run(
   solver: "SolverPy",
   bid: str,
   sid: str,
   desc: str | None = None,
   taskdone: Any = None,
   db: "DB | None" = None,
   cores: int = 4,
   shuffle: bool = True,
   force: bool = False,
   solvedby: str | None = None,
   it: int | None = None,
   **others: Any,
) -> "Result":
   others = dict(others, force=force, it=it, solvedby=solvedby)
   desc = desc if desc else jobname(solver, bid, sid)
   logger.debug(f"evaluating {desc}: {jobname(solver, bid, sid)}")
   # prepare the tasks to be evaluated
   ps = bids.problems(bid)
   skipped = {}
   if solvedby and (it == 0):
      solvable = Solved(bid, solvedby, solver._limits.limit).cache
      if solvable:
         simulate = dict(status="TIMEOUT",
                         runtime=solver._limits.timeout,
                         limit=solver._limits.limit)
         skipped = {p: dict(simulate) for p in (set(ps) - solvable)}
         if taskdone:
            for (_p, res) in skipped.items():
               taskdone(solver.solved(res))
         if db:
            tasks0 = [SolverTask(solver, bid, sid, p) for p in skipped]
            results = [simulate] * len(tasks0)
            db.store(tasks0, results)
         ps = solvable
         logger.debug(
            f"evaluation: restricted to {len(solvable)} problems solvable by {solvedby}"
         )
   #solvable = None
   #if solvedby and (it == 0):
   #   solvable = Solved(bid, solvedby, solver.limits.limit).cache
   #   if solvable:
   #      logger.debug(f"evaluation: restricted to {len(solvable)} problems solvable by {solvedby}")
   #ps = solvable if solvable else bids.problems(bid)
   tasks = [SolverTask(solver, bid, sid, p) for p in ps]
   logger.debug(f"evaluation: {len(tasks)} tasks scheduled")
   # check for the (cached) results in the database
   if db and not force:
      done = db.query(tasks)
      todo = [t for t in tasks if t not in done]
      if taskdone:
         for (task, result) in done.items():
            taskdone(task.status(result))
      done = {t.problem: res for (t, res) in done.items()}
   else:
      done = {}
      todo = tasks
   # evaluate the remaining tasks
   if db and force:
      logger.debug(f"forced evaluation: db not queried")
   else:
      logger.debug(f"evaluation: {len(todo)} tasks remain to be evaluated")
   if todo:
      if shuffle:
         logger.debug(f"shuffling tasks")
         random.shuffle(todo)
      bar = SolvingBar(len(todo), desc, miniters=1)
      results = launcher.launch(
         todo,
         bar=bar,
         taskdone=taskdone,
         cores=cores,
         **others,
      )
      # store the new results in the database
      if db: db.store(todo, results)
      # compose the cached and new results
      results = {t.problem: res for (t, res) in zip(todo, results)}
      results.update(done)
      results.update(skipped)
      logger.debug(
         f"evaluation done: +{bar._solved} -{bar._unsolved} !{bar._errors}")
   else:
      logger.debug("evaluation skipped: already done")
      if db:
         db.commit()  # update cached results (eg. generate `solved`)
      results = done
   return results


def launch(
   solver: "SolverPy",
   bidlist: list[str],
   sidlist: list[str],
   ref: (bool | int | str | None) = None,
   sidnames: bool = True,
   cores: int = 4,
   **others: Any,
) -> dict["SolverJob", "Result"]:
   # initialize jobs and compute label width
   logger.debug("evaluation started")
   refjob = None
   if ref is True:
      refjob = (solver, bidlist[0], sidlist[0])
   elif type(ref) is int:
      refjob = (solver, bidlist[0], sidlist[ref])
   jobs = [(solver, bid, sid) for bid in bidlist for sid in sidlist]
   total = sum(len(bids.problems(bid)) for (s, bid, _sid) in jobs)
   (nicks, totaldesc, report) = legend(jobs, refjob, sidnames=sidnames)
   logger.info(
      f"Evaluating {len(jobs)} jobs with {total} tasks together:\n{report}")
   totbar = RunningBar(total, totaldesc, miniters=1)
   # run the jobs one by one
   allres: dict["SolverJob", "Result"] = {}
   try:
      for job in jobs:
         result1 = run(
            *job,
            taskdone=totbar.status,
            desc=nicks[job],
            cores=cores,
            **others,
         )
         allres[job] = result1  # (bid,sid) should be a primary key
      totbar.close()
      if totbar._errors:
         logger.error(
            f"There were errors: {totbar._errors} tasks failed to evaluate.")
   except KeyboardInterrupt as e:
      totbar.close()
      raise e

   report = summary(allres, nicks, refjob)
   logger.info(f"Evaluation done:\n{report}")
   return allres


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


def summary(
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
