import os, json
import logging

from .provider import Provider
from ..path import bids

logger = logging.getLogger(__name__)

NAME = "results"

class Jsons(Provider):

   def __init__(self, bid, sid):
      Provider.__init__(self, bid, sid)
      self.cache = {}
      self.load()

   def simulate(self, task, result):
      timeout = task.solver.timeout
      if "timeout" in result:
         # the cached result is timeout
         if result["timeout"] < timeout:
            # recompute since we have more time
            return None
      else:
         # the cached result is solved
         if result["runtime"] > timeout:
            # simulated timeout
            return dict(result, status="TIMEOUT", runtime=timeout, timeout=timeout)
      return result

   def query(self, task):
      self.check(task)
      if task.problem in self.cache:
         result = self.cache[task.problem] 
         return task.solver.simulate(result)
      return None

   def store(self, task, result):
      self.check(task)
      if task.solver.valid(result):
         self.cache[task.problem] = result

   def check(self, task):
      if (self.bid != task.bid) or (self.sid != task.sid):
         raise Exception("Error: Operation on invalid bid/sid in a provider.")

   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid),
         self.sid).rstrip("/") + ".json"

   def load(self):
      f = self.cachepath()
      logger.debug(f"json loading {f}")
      if os.path.isfile(f):
         with open(f) as fr:
            self.cache = json.load(fr)
      else:
         self.cache = {}
      logger.debug(f"json loaded {len(self.cache)} entries")

   def commit(self):
      f = self.cachepath()
      logger.debug(f"json writing {f}")
      os.makedirs(os.path.dirname(f), exist_ok=True)
      with open(f,"w") as fw:
         json.dump(self.cache, fw, indent=3, sort_keys=True)
      logger.debug(f"json saved {len(self.cache)} entries")

