import os
import logging
import multiprocessing

from ..decorator import Decorator
from ....benchmark.path import bids

NAME = "trains"

logger = logging.getLogger(__name__)

class Trains(Decorator):

   def __init__(self, dataname, filename="train.in"):
      self.lock = multiprocessing.Manager().Lock()
      self._file = os.path.join(bids.dbpath(NAME), dataname, filename)
   
   def register(self, solver):
      super().register(solver)
      self.solver = solver

   def finished(self, instance, strategy, output, result):
      if not (output and self.solver.solved(result)):
         return
      samples = self.extract(instance, strategy, output, result)
      self.save(instance, strategy, samples)

   def extract(self, instance, strategy, output, result):
      raise NotImlementedError

   def save(self, instance, strategy, samples):
      if not samples:
         return
      self.lock.acquire()
      os.makedirs(os.path.dirname(self._file), exist_ok=True)
      with open(self._file, "a") as fa:
         try:
            fa.write(samples)
            self.stats(instance, strategy, samples)
         finally:
            self.lock.release()
    
   def stats(self, instance, strategy, samples):
      with open(self._file+"-stats", "a") as infa:
        count = samples.count("\n")
        infa.write(f"{instance} {strategy}: {count}\n")

