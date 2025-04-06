
def par2score(solver, result):
   if result and ("runtime" in result) and solver.solved(result):
      # NOTE: timeouts after solving when dumping proof happen
      #       (then "runtime" might not be filled)
      return result["runtime"] 
   else:
      return 2 * solver.limits.timeout

def summary(solver, bid, sid, results, refsolved=None, refpar2=None):
   solved = set()
   errors = 0
   unsolved = 0
   timeouts = 0
   par2 = 0
   solves = set()
   for (problem,res) in results.items():
      par2 += par2score(solver, res)
      if solver.solved(res): 
         solved.add(problem)
      elif not solver.valid(res): 
         errors += 1
      elif res["status"] in solver.timeouts: 
         timeouts += 1
      else: 
         unsolved += 1
      
   #errors = [p for (p,r) in results.items() if solver.
   if refsolved is None:
      par2 = f"{par2:0.2f}"
      return (len(solved), par2, unsolved, timeouts, errors)
   else:
      par2plus = (refpar2 - par2) / (refpar2 / 100.0)
      par2plus = f"{par2plus:+0.2f}%"
      par2 = f"{par2:0.2f}"
      plus = len(solved - refsolved)
      minus = len(refsolved - solved)
      return (len(solved), plus, minus, par2, par2plus, unsolved, timeouts, errors)

