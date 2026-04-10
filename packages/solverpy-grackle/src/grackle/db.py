import json
from os import path

class DB:
   def __init__(self, name, rank):
      self.name = name
      self.insts = []      # all instances
      self.results = {}    # { conf : {inst:[quality,runtime,..]} }
      self.ranking = {}    # { inst : [conf] }
      self.runner = None
      self.rank = rank
      self.load("cache")

   def load(self, prefix):
      f_results = "db-%s-%s.json" % (self.name,prefix)
      if path.isfile(f_results):
         self.results = json.load(open(f_results))

   def save(self, prefix):
      f_results = "db-%s-%s.json" % (self.name,prefix)
      json.dump(self.results, open(f_results,"w"), indent=3, sort_keys=True)

   def update(self, confs):
      # collect (conf,inst) pairs to evaluate
      cis = []
      for conf in confs:
         if conf not in self.results:
            self.results[conf] = {}
         for inst in self.insts:
            if inst not in self.results[conf]:
               cis.append((conf,inst))
  
      # evaluate them
      if cis:
         outs = self.runner.runs(cis)
         for ((conf,inst),result) in outs:
            self.results[conf][inst] = result
  
      # udpate ranking for each instance
      self.update_ranking(confs)

   def update_ranking(self, confs):
      self.ranking = {}
      for inst in self.insts:
         key = lambda conf: (self.results[conf][inst][0], conf)
         #oks = [c for c in confs if self.results[c][inst] and self.results[c][inst][0] != failed]
         oks = [c for c in confs if self.results[c][inst] and self.runner.success(self.results[c][inst][2])]
         self.ranking[inst] = sorted(oks, key=key)

   def mastered(self, conf):
      return [i for i in self.insts if conf in self.ranking[i][:self.rank]]

   def status(self, failed=1000000000):
      total = 0
      qsum = 0.0
      tsum = 0.0
      suc = 0
      qsumsuc = 0.0
      tsumsuc = 0.0
      success = set()
      for conf in self.results:
         for inst in self.insts:
            result = self.results[conf][inst]
            result = result if result else (failed, 0, "error")
            qsum += result[0]
            tsum += result[1]
            total += 1
            if self.runner.success(result[2]): # result[0] != failed:
               qsumsuc += result[0]
               tsumsuc += result[1]
               suc += 1
               success.add(inst)
      return (self.name, len(success), qsumsuc/suc, tsumsuc/suc, qsum/total, tsum/total)

