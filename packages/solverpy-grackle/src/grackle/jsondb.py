import json

SOLVED = ['Satisfiable', 'Unsatisfiable', 'Theorem', 'CounterSatisfiable', 'ContradictoryAxioms', 'sat', 'unsat']

def transcript(fin):
   try:
      lines = [line.split() for line in open(fin).read().strip().split("\n")]
   except OSError:
      return None
   lines = {line[4]: line[-1] for line in lines}
   return lines

def load(f, f_trans=None, filter_mode=None, f_restrict=None): 
   # `filter_mode` is `None`, `True`, or `False`.
   res = json.load(open(f))
   if f_restrict:
      probs = set(open(f_restrict).read().strip().split("\n"))
      res = {c:{p:r for (p,r) in res[c].items() if p in probs} for c in res}
   if f_trans:
      renames = transcript(f_trans)
      if renames:
         if filter_mode is not None:
            res = {s:res[s] for s in res if (s in renames) is filter_mode}
         res = {(renames[s] if s in renames else s):res[s] for s in res}
   return res

def update(todb, fromdb):
   news = fromdb.keys() - todb.keys()
   #both = fromdb.keys() & todb.keys()
   for s in news:
      todb[s] = fromdb[s] 

def join(dbs, prefs=None):
   prefs = prefs if prefs else [None for x in dbs]
   joint = {}
   for (db, pref) in zip(dbs, prefs):
      js = load(db)
      if pref:
         js = {(pref+x):js[x] for x in js}
      update(joint, js)
   return joint

def solved1(result, limit=None):
   def is_solved(res):
      if not res: return False
      return res[2] in SOLVED and ((res[1]<=limit) if limit else True)
   return set(p for p in result if is_solved(result[p]))

def solved(results, apply=solved1, limit=None):
   return {s:apply(results[s],limit) for s in results}

def counts(results, limit=None):
   return solved(results, apply=lambda r,l: len(solved1(r,l)), limit=limit)

def solves(results, solved0=None, limit=None):
   solved0 = solved0 if solved0 else solved(results, limit=limit)
   probs = frozenset(p for c in results for p in results[c])
   probs = {p:frozenset(c for c in results if p in solved0[c]) for p in probs}
   return probs

def scores(results, fellows, solved0=None, limit=None):
   fellows = {x:results[x] for x in fellows}
   solved0 = solved(fellows, limit=limit) if not solved0 else solved0
   solves0 = solves(fellows, solved0, limit=limit)

   #morsel = lambda p: len(fellows) / len(solves0[p])
   #morsel = lambda p: (1 / len(solves0[p])) 
   #morsel = lambda p: (len(fellows)/len(solves0[p])) * (1/(len(fellows)**1)) 
   morsel = lambda p: (len(fellows)/len(solves0[p])) * (1/(2**(len(fellows)-1))) 
   #morsel = lambda p: (1/len(solves0[p])) * (1/(len(fellows)**2)) 
   score = lambda c: sum(morsel(p) for p in solved0[c])
   #score = lambda c: sum(morsel(p) for p in solved0[c])/len(solved0[c])
   return {c:score(c) for c in fellows}

def similars(results, fellows, solves0=None, limit=None):
   solves0 = solves0 if solves0 else solves({x:results[x] for x in fellows}, limit=limit) 
   sims = {x:{} for x in fellows}
   for p in solves0:
      linked = solves0[p]
      for (s,t) in [(s,t) for s in linked for t in linked if s!=t]:
         if t not in sims[s]: sims[s][t] = 0
         sims[s][t] += 1
   return sims


# printing
#
#

def perf(counts):
   data = [(counts[s], s) for s in sorted(counts, key=lambda x: counts[x])]
   print("\n".join("%s\t%s" % x for x in data))

def greedy(results, max_n=None):
   cover = []
   total = 0
   n = 0
   while results:
      best = max(results, key=lambda s: len(results[s]))
      cover.append(best)
      eaten = frozenset(results[best])
      total += len(eaten)
      n += 1
      print("%s: %s" % (best, len(eaten)))
      for s in results:
         results[s].difference_update(eaten)
      results = {s:results[s] for s in results if results[s]}
      if max_n and n >= max_n:
         break
   print("# TOTAL = %s (by %d)" % (total, n))
   return cover
   
