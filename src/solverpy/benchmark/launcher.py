import os
import logging

from ..benchmark.path import bids
from ..tools import human
from ..task.solvertask import SolverTask
from ..task.bar import SolvingBar, RunningBar
from ..task import launcher 
from .report import markdown

logger = logging.getLogger(__name__)

def jobname(solver, bid, sid):
   return f"{solver}:{sid} @ {bid}"

def run(solver, bid, sid, desc=None, taskdone=None, db=None, **others):
   desc = desc if desc else jobname(solver, bid, sid)
   logger.debug(f"evaluating {desc}: {jobname(solver, bid, sid)}")
   # prepare the tasks to be evaluated
   ps = bids.problems(bid)
   tasks = [SolverTask(solver,bid,sid,p) for p in ps]
   logger.debug(f"evaluation: {len(tasks)} tasks scheduled")
   # check for the (cached) results in the database
   if db:
      done = db.query(tasks)
      todo = [t for t in tasks if t not in done]
      if taskdone:
         for (task,result) in done.items():
            taskdone(task.status(result))
      done = {t.problem:res for (t,res) in done.items()}
   else:
      done = {}
      todo = tasks
   # evaluate the remaining tasks
   logger.debug(f"evaluation: {len(todo)} tasks remain to be evaluated")
   if todo:
      bar = SolvingBar(len(todo), desc)
      results = launcher.launch(todo, bar=bar, taskdone=taskdone, **others)
      # store the new results in the database
      if db: db.store(todo, results)
      # compose the cached and new results
      results = {t.problem:res for (t,res) in zip(todo, results)}
      results.update(done)
      logger.debug(f"evaluation done: +{bar._solved} -{bar._unsolved} !{bar._errors}")
   else:
      logger.debug("evaluation skipped: already done")
      results = done
   return results

def launch(solver, bidlist, sidlist, ref=None, **others):
   # initialize jobs and compute label width
   logger.debug("evaluation started")
   if ref is True:
      ref = (solver, bidlist[0], sidlist[0])
   jobs = [(solver,bid,sid) for bid in bidlist for sid in sidlist]
   total = sum(len(bids.problems(bid)) for (s,bid,sid) in jobs)
   (nicks, totaldesc, report) = legend(jobs, ref)
   logger.info(f"Evaluating {len(jobs)} jobs with {total} tasks together:\n{report}")
   totbar = RunningBar(total, totaldesc)
   # run the jobs one by one
   allres = {}
   try:
      for job in jobs:
         result1 = run(*job, taskdone=totbar.status, desc=nicks[job], **others)
         allres[job] = result1 # (bid,sid) should be a primary key
      totbar.close()
      if totbar._errors:
         logger.error(f"There were errors: {totbar._errors} tasks failed to evaluate.")
   except KeyboardInterrupt as e:
      totbar.close()
      raise e
   
   report = summary(allres, nicks, ref)
   logger.info(f"Evaluation done:\n{report}")
   return allres



def legend(jobs, ref=None):
   width = len(str(len(jobs)-1))
   total = "*" * width
   total = f"[{total}/{len(jobs)-1}]"
   nicks = {}
   header = ["job", "solver", "benchmark", "strategy"]
   rows = []
   for (n,job) in enumerate(jobs):
      (solver, bid, sid) = job
      if ref == job:
         nick = "ref"
      else:
         nick = f"{n:{width}}/{len(jobs)-1}"
      nicks[job] = nick
      rows.append([nick, solver.name, bid, sid])

   report = [""]
   report += markdown.heading("Legend", level=3)
   report += markdown.table(header, rows)
   report += [""]
   report = markdown.dump(report, prefix="> ")
   return (nicks, total, report)

def summary(allres, nicks, ref=None):
   report  = [""]
   report += markdown.heading("Summary", level=3)
   report += markdown.summary(allres, nicks, ref=ref)
   report += [""]
   return markdown.dump(report, prefix="> ")

