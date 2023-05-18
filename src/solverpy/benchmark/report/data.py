
def summary(solver, bid, sid, results, refsolved=None):
   solved = set()
   errors = 0
   unsolved = 0
   timeouts = 0
   solves = set()
   for (problem,res) in results.items():
      if solver.solved(res): solved.add(problem)
      elif not solver.valid(res): errors += 1
      elif res["status"] in solver.timeouts: timeouts += 1
      else: unsolved += 1
      
   #errors = [p for (p,r) in results.items() if solver.
   if refsolved is None:
      return (len(solved), unsolved, timeouts, errors)
   else:
      plus = len(solved - refsolved)
      minus = len(refsolved - solved)
      return (len(solved), plus, minus, unsolved, timeouts, errors)

