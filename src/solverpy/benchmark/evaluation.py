from typing import Any, TYPE_CHECKING
import random
import logging

from .path import bids
from ..tools import log
from ..task.solvertask import SolverTask
from ..task.talker import Talker
from ..task.logtalker import LogTalker
from ..task import launcher
from .reports import markdown
from .db.providers.solved import Solved
from ..setups.setup import Setup

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


def run(
   job: "SolverJob",
   talker: Talker,
   db: "DB | None" = None,
   cores: int = 4,
   shuffle: bool = True,
   force: bool = False,
   solvedby: str | None = None,
   it: int | None = None,
   proofs: dict[str, int] | None = None,
   max_proofs: int = 0,
   **others: Any,
) -> "Result":
   others = dict(others, force=force, it=it, solvedby=solvedby)
   talker.next(job)
   (solver, bid, sid) = job
   #logger.debug(f"evaluating {jobname(solver, bid, sid)}")

   todo: list["SolverTask"] = []
   skipped: dict[str, "Result"] = {}
   done: dict[str, "Result"] = {}
   results: dict[str, "Result"] = {}
   cnt_dis: int = 0

   def restrict_problems(ps: list[str]) -> list[str]:
      nonlocal skipped, talker
      if (not solvedby) or (it != 0):
         return ps
      solvable = Solved(bid, solvedby, solver._limits.limit).cache
      if not solvable:
         return ps
      simulate = dict(
         status="TIMEOUT",
         runtime=solver._limits.timeout,
         limit=solver._limits.limit,
      )
      skipped = {p: dict(simulate) for p in (set(ps) - solvable)}
      for (problem, result) in skipped.items():
         talker.finished(SolverTask(solver, bid, sid, problem), result)
      if db:
         tasks0 = [SolverTask(solver, bid, sid, p) for p in skipped]
         results = [simulate] * len(tasks0)
         db.store(tasks0, results)
      ps = list(solvable)
      logger.debug(
         f"evaluation: restricted to {len(solvable)} problems solvable by {solvedby}"
      )
      return ps

   def enable_trains(p: str) -> str:
      nonlocal cnt_dis
      if max_proofs and proofs and (p in proofs):
         if proofs[p] >= max_proofs:
            cnt_dis += 1
            return "disable"
      return "enable"

   def schedule_tasks(ps: list[str]) -> list["SolverTask"]:
      nonlocal cnt_dis
      tasks = [
         SolverTask(
            solver,
            bid,
            sid,
            p,
            calls=[
               ("trains", "disable", [], {}),
               ("debug-trains", "disable", [], {}),
            ] if enable_trains(p) == "disable" else [],
         ) for p in ps
      ]
      logger.debug(f"evaluation: {len(tasks)} tasks scheduled")
      logger.debug(f"evaluation: trains disabled for {cnt_dis} problems")
      return tasks

   def check_cache(tasks: list["SolverTask"]):
      nonlocal todo, done
      # check for the (cached) results in the database
      if db and not force:
         done0 = db.query(tasks)
         todo = [t for t in tasks if t not in done0]
         for (task, result) in done0.items():
            talker.finished(task, result)
         done = {t.problem: res for (t, res) in done0.items()}
      else:
         done = {}
         todo = tasks
      # evaluate the remaining tasks
      if db and force:
         logger.debug(f"forced evaluation: db not queried")
      else:
         logger.debug(f"evaluation: {len(todo)} tasks remain to be evaluated")

   def launch_evaluation() -> list["Result"]:
      nonlocal todo, done, results
      if not todo:
         logger.debug("evaluation skipped: already done")
         if db:
            # update cached results (eg. generate `solved`)
            db.commit()
         results = done
         return []
      if shuffle:
         logger.debug(f"shuffling tasks")
         random.shuffle(todo)
      results0 = launcher.launch(
         todo,
         talker=talker,
         cores=cores,
         **others,
      )
      return results0

   def update_results(results0: list["Result"]):
      nonlocal results, todo, done, skipped
      # store the new results in the database
      if db: db.store(todo, results0)
      # compose the cached and new results
      results = {t.problem: res for (t, res) in zip(todo, results0)}
      if max_proofs:
         assert proofs is not None
         for (p, res) in results.items():
            if solver.solved(res):
               if p not in proofs:
                  proofs[p] = 0
               proofs[p] += 1
      results.update(done)
      results.update(skipped)

   # main evaluation of `solver` on `bid` and `sid`
   ps = restrict_problems(bids.problems(bid))
   tasks = schedule_tasks(ps)
   check_cache(tasks)
   results0 = launch_evaluation()
   if results0:
      update_results(results0)
   return results


def launch(
   solver: "SolverPy",
   bidlist: list[str],
   sidlist: list[str],
   ref: (bool | int | str | None) = None,
   sidnames: bool = True,
   cores: int = 4,
   talker: Talker | None = None,
   **others: Any,
) -> dict["SolverJob", "Result"]:

   jobs: list["SolverJob"] = []
   nicks: dict["SolverJob", str] = {}
   refjob = None
   talker = talker or LogTalker()

   def initialize_jobs():
      nonlocal jobs, nicks, refjob
      logger.debug("evaluation started")
      if ref is True:
         refjob = (solver, bidlist[0], sidlist[0])
      elif type(ref) is int:
         refjob = (solver, bidlist[0], sidlist[ref])
      jobs = [(solver, bid, sid) for bid in bidlist for sid in sidlist]
      talker.begin(jobs, refjob=refjob, sidnames=sidnames)

   def launch_jobs() -> dict["SolverJob", "Result"]:
      nonlocal nicks, jobs, refjob, talker
      assert talker
      allres = {}
      try:
         for job in jobs:
            result1 = run(
               job,
               talker=talker,
               cores=cores,
               **others,
            )
            allres[job] = result1  # (bid,sid) should be a primary key
         talker.end(allres, refjob=refjob)
      except KeyboardInterrupt:
         talker.terminate()
         raise
      return allres

   initialize_jobs()
   allres = launch_jobs()
   return allres
