import logging

from ...solver.object import SolverPyObj
from ...benchmark.path import bids

logger = logging.getLogger(__name__)

class DB(SolverPyObj):

   def __init__(self, providers):
      SolverPyObj.__init__(self)
      self._providers = providers
      self.loaded = {}

   def represent(self):
      return dict(
         path=bids.dbpath(),
         providers=self._providers
      ) 

   def connect(self, bid, sid, limit):
      if (bid,sid) not in self.loaded:
         logger.debug(f"connecting providers for {sid} @ {bid}")
         insts = [maker(bid,sid,limit) for maker in self._providers]
         self.loaded[(bid,sid)] = insts
         logger.debug(f"connected to {len(insts)} providers")

   def providers(self, task):
      return self.loaded[(task.bid,task.sid)]

   def commit(self):
      for key in self.loaded:
         logger.debug(f"db commit: {key}")
         for provider in self.loaded[key]:
            provider.commit()

   def querytask(self, task):
      self.connect(task.bid, task.sid, task.solver.limits.limit)
      for provider in self.providers(task):
         provider.check(task)
         result = provider.query(task)
         if result:
            return result
      return None
   
   def cachedtask(self, task, result):
      self.connect(task.bid, task.sid, task.solver.limits.limit)
      for provider in self.providers(task):
         provider.check(task)
         provider.cached(task, result)

   def storetask(self, task, result):
      self.connect(task.bid, task.sid, task.solver.limits.limit)
      for provider in self.providers(task):
         provider.check(task)
         provider.store(task, result)

   def query(self, tasks):
      logger.debug(f"db query on {len(tasks)} tasks")
      results = {}
      for task in tasks:
         result = self.querytask(task)
         if result:
            results[task] = result
      logger.debug(f"announcing {len(results)} cached results")
      for (task, result) in results.items():
         self.cachedtask(task, result)
      logger.debug(f"db query done: {len(results)} tasks already done")
      return results

   def store(self, tasks, results):
      logger.debug(f"db store on {len(tasks)} tasks")
      count = 0
      for (task, result) in zip(tasks, results):
         self.storetask(task, result)
         count += 1
      self.commit()
      logger.debug(f"db store done: {count} commits")

