import os

from ..path import bids, sids
from ..tools import par, bars


def prove1(solver, instance, strategy):
   result = solver.solve(instance, strategy)
   return (instance, result)

def eval1(solver, bid, sid, cores=4, chunksize=1, **others):
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

   bar = bars.solved(total=len(args), desc=sid)
   par.apply(prove1, args, cores=cores, bar=bar, chunksize=chunksize, callback=callback)
   return results

#def evals(prover, bids, sids, cores=4, **others):
#   allres = {}
#   ns = len(bids) * len(sids)
#   ps = sum([len(problem.problems(bid)) for bid in bids]) * len(sids)
#   logger.info("+ evaluating %s strategies on %d benchmarks" % (len(sids), len(bids)))
#   logger.debug(log.data("- evaluation parameters:", dict(
#      bids=bids, 
#      sids=sids,
#      cores=cores,
#      prover=prover.name(),
#      resources=prover.resources(),
#      problems=human.humanint(ps),
#      eta=human.humantime(ps*prover.timeout()/cores) if prover.timeout() else "unknown",
#   )))
#   
#   n = 1
#   label = "(%%3d/%d)" % ns
#   for bid in bids:
#      for sid in sids:
#         result1 = eval1(prover, bid, sid, cores=cores, label=label%n, **others)
#         n += 1
#         result1 = {(bid,sid,p):result1[p] for p in result1}
#         allres.update(result1)
#   return allres

