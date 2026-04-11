import numpy
from scipy import spatial
from . import log

def init(state):
   f_in = state.unsolved["features"]
   insts = frozenset(state.trains.insts)
   
   features = {}
   maxs = None
   length = None
   found = set()
   for line in open(f_in):
      parts = line.strip().split("\t")
      name = parts[0]
      if name not in insts:
         continue
      vector = list(map(float, parts[1:]))
      if not length:
         length = len(vector)
      else:
         if length != len(vector):
            raise Exception("Different feature vector lengths.")
      if not maxs:
         maxs = list(vector)
      else:
         maxs = [max(maxs[i], vector[i]) for i in range(len(vector))]
      found.add(name)
      features[name] = numpy.array(vector)

   missing = insts - found
   if missing:
      log.missing(missing)
      raise Exception("Missing features for some training instances.")

   maxs = numpy.array(maxs)
   state.features = {i:scale(features[i],maxs) for i in features}
   state.scale = maxs
   state.kdtree = None
   state.kdindices = None

def scale(data, maxs):
   return 1000 * (data / maxs)

def update(state, conf):
   mode = state.unsolved["mode"]
   if mode == "inits" and state.kdtree:
      return
   if mode in ["inits", "all"]:
      confs = state.alls
   elif mode == "actives":
      confs = state.active
   else: # mode == "current"
      confs = [conf]
   db = state.trains
   confs = [c for c in confs if c in db.results]
   solved = lambda c, i: db.runner.success(db.results[c][i][2])
   oks = [i for c in confs for i in db.results[c] if solved(c,i)]
   uns = sorted(frozenset(db.insts) - frozenset(oks))
   if not uns:
      return False
   data = numpy.array([state.features[i] for i in uns])
   log.kdtree(data)
   state.kdtree = spatial.KDTree(data)
   state.kdindices = dict(enumerate(uns))
   return True

def closest(state, dists, idxs, count):
   idxs = list(zip(*idxs)) # this does unzip or transpose
   idxs.reverse() # for efficiency (list.pop() is O(1) but list.pop(0) is O(n))
   selected = []
   info = {}
   rank = 0
   while idxs:
      col = list(enumerate(idxs.pop())) # the problems in distance `rank`
      col.sort(key=lambda c: dists[c[0]][rank]) # sort by distances
      for (n,idx) in col:
         if idx in info:
            continue
         selected.append(idx)
         info[idx] = (n, rank)
         if len(selected) >= count:
            break # break the outer loop
      else:
         rank += 1
         if rank >= state.unsolved["maxrank"]:
            break
         else:
            continue
      break
   return (selected, info)

def select(state, conf, insts):
   if not state.unsolved:
      return []
   if not update(state, conf):
      log.kdnone()
      return []
   insts = sorted(insts)
   query = numpy.array([state.features[i] for i in insts])
   uns = len(state.kdindices)
   (dists, idxs) = state.kdtree.query(query, k=uns)
   count = min(uns, int(len(insts) * state.unsolved["ratio"]))
   (selected, info) = closest(state, dists, idxs, count)
   log.kdselect(state, conf, insts, selected, info)
   return [state.kdindices[idx] for idx in selected]

