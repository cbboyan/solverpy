import os
import logging

from ..benchmark.path import bids
from ..tools import human
from ..task.solvertask import SolverTask
from ..task.bar import SolvingBar, RunningBar
from ..task import launcher 

logger = logging.getLogger(__name__)

def run(solver, bid, sid, desc=None, taskdone=None, db=None, **others):
   desc = desc if desc else f"{solver}:{sid} @ {bid}"
   logger.debug(f"evaluating {desc}: {solver}:{sid} @ {bid}")
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

def legend(jobs):
   width = len(str(len(jobs)-1))
   legs = [(f"{s}:{sid} @ {bid}", f"[{n:{width}}/{len(jobs)-1}]") for (n,(s,bid,sid)) in enumerate(jobs)]
   desc = "*" * width
   desc = f"[{desc}/{len(jobs)-1}]"
   txt = "\n".join(f"> {short} {long}" for (long,short) in legs)
   return (legs, desc, txt)

def launch(solver, bidlist, sidlist, **others):
   # initialize jobs and compute label width
   logger.debug("evaluation started")
   jobs = [(solver,bid,sid) for bid in bidlist for sid in sidlist]
   allres = {}
   nicks = {}
   total = sum(len(bids.problems(bid)) for (s,bid,sid) in jobs)
   (legs, desc, txt) = legend(jobs)
   logger.info(f"Evaluating {len(jobs)} jobs with {total} tasks together:\n{txt}")
   totbar = RunningBar(total, desc)
   # run the jobs one by one
   try:
      for ((solver,bid,sid),(_,desc)) in zip(jobs,legs):
         result1 = run(solver, bid, sid, taskdone=totbar.status, desc=desc, **others)
         allres[(solver,bid,sid)] = result1 # (bid,sid) should be a primary key
         nicks[(solver,bid,sid)] = desc
      totbar.close()
      if totbar._errors:
         logger.error(f"There were errors: {totbar._errors} tasks failed to evaluate.")
   except KeyboardInterrupt as e:
      totbar.close()
      raise e
   logger.info("Evaluation done.")
   report(allres, nicks)
   return allres

def summary(solver, bid, sid, results):
   solved = 0
   errors = 0
   unsolved = 0
   timeouts = 0
   for (problem,res) in results.items():
      if solver.solved(res): solved += 1
      elif not solver.valid(res): errors += 1
      elif res["status"] in solver.timeout: timeouts += 1
      else: unsolved += 1
      
   #errors = [p for (p,r) in results.items() if solver.
   return (solved, unsolved, timeouts, errors)

def report(allres, nicks):
   sums = []
   width = 0
   for ((solver,bid,sid),res) in allres.items():
      s = summary(solver, bid, sid, res)
      sums.append(s+(nicks[(solver,bid,sid)],))
      width = max(width, max(s))
   width = len(str(width))
   sums.sort(reverse=True)
   for (solved, unsolved, timeouts, errors, nick) in sums:
      print(f"> | {nick:{width}} | {solved:{width}} | {unsolved:{width}} | {timeouts:{width}} | {errors:{width}} |")
   

