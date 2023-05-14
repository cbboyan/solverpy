import logging

logger = logging.getLogger(__name__)

class DB:

   def __init__(self, providers):
      self._providers = providers
      self.loaded = {}

   def connect(self, bid, sid):
      if (bid,sid) not in self.loaded:
         logger.debug(f"connecting providers for {sid} @ {bid}")
         insts = [maker(bid,sid) for maker in self._providers]
         self.loaded[(bid,sid)] = insts
         logger.debug(f"connected to {len(insts)} providers")

   def providers(self, task):
      return self.loaded[(task.bid,task.sid)]

   def commit(self, bid, sid):
      for provider in self.loaded[(bid,sid)]:
         provider.commit()

   def querytask(self, task):
      self.connect(task.bid, task.sid)
      for provider in self.providers(task):
         result = provider.query(task)
         if result:
            return result
      return None

   def storetask(self, task, result):
      self.connect(task.bid, task.sid)
      for provider in self.providers(task):
         provider.store(task, result)

   def query(self, tasks):
      logger.debug(f"db query on {len(tasks)} tasks")
      results = {}
      for task in tasks:
         result = self.querytask(task)
         if result:
            results[task] = result
      logger.debug(f"db query done: {len(results)} tasks already done")
      return results

   def store(self, tasks, results):
      logger.debug(f"db store on {len(tasks)} tasks")
      tocommit = set()
      for (task, result) in zip(tasks, results):
         self.storetask(task, result)
         tocommit.add((task.bid,task.sid))
      for (bid,sid) in tocommit:
         self.commit(bid, sid)
      tc = ", ".join(f"{s} @ {b}" for (b,s) in sorted(tocommit))
      logger.debug(f"db store done: {len(tocommit)} commits {tc}")

