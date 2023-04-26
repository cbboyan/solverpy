import os

from ..path import bids, sids
from ..tools import par, bars


def prove1(solver, instance, strategy):
   result = solver.solve(instance, strategy)
   return (instance, result)

def eval1(solver, bid, sid, cores=4, chunksize=1, desc=None, taskdone=None, **others):
   ps = bids.problems(bid)
   args = [(solver, (bid, p), sid) for p in ps]
   results = {}

   def callback(res, bar):
      nonlocal solver, results
      ((bid,p), result) = res
      results[p] = result
      if not solver.valid(result):
         bar.update_errors()
      elif solver.solved(result):
         bar.update_solved()
      else:
         bar.update_failed()
      if taskdone is not None:
         taskdone()
 
   desc = "%s @ %s" % (sid, bid) if not desc else desc
   bar = bars.solved(total=len(args), desc=desc)
   par.apply(prove1, args, cores=cores, bar=bar, chunksize=chunksize, callback=callback)
   solver.flush()
   return results

def evals(jobs, **others):
   
   def indent(desc, left=True):
      nonlocal maxdesc
      if left:
         return (" " * (maxdesc-len(desc))) + desc
      else:
         return desc + (" " * (maxdesc-len(desc))) 

   allres = {}
   total = 0
   maxdesc = 0
   for (solver, bid, sid) in jobs:
      total += len(bids.problems(bid))
      desc = "%s @ %s" % (sid, bid)
      maxdesc = max(maxdesc, len(desc))

   desc = "Total: %s jobs, %s tasks" % (len(jobs), total)
   maxdesc = max(maxdesc, len(desc))
   totbar = bars.default(total, indent(desc, left=False))
   
   for (solver, bid, sid) in jobs:
      desc = "%s @ %s" % (sid, bid)
      result1 = eval1(solver, bid, sid, taskdone=lambda: totbar.update(1), desc=indent(desc), **others)
      result1 = {(bid,sid,p):result1[p] for p in result1}
      allres.update(result1)
   totbar.close()
   
   return allres

