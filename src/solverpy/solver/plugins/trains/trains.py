import os
import logging
import multiprocessing

from ..decorator import Decorator
from ....benchmark.path import bids

NAME = "trains"

logger = logging.getLogger(__name__)

class Trains(Decorator):

   def __init__(self, dataname, filename="train.in"):
      self._lock = multiprocessing.Manager().Lock()
      self.reset(dataname, filename)
   
   def reset(self, dataname=None, filename="train.in"):
      if dataname:
         self._dataname = dataname
      self._filename = filename

   def path(self, dataname=None, filename=None):
      dataname = dataname or self._dataname
      filename = filename or self._filename
      return os.path.join(bids.dbpath(NAME), dataname, filename)

   def register(self, solver):
      super().register(solver)
      self._solver = solver

   def finished(self, instance, strategy, output, result):
      if not (output and self._solver.solved(result)):
         return
      samples = self.extract(instance, strategy, output, result)
      self.save(instance, strategy, samples)

   def extract(self, instance, strategy, output, result):
      "Extract training samples from `output`."
      raise NotImlementedError
   
   def save(self, instance, strategy, samples):
      if not samples:
         return
      self._lock.acquire()
      try:
         os.makedirs(os.path.dirname(self.path()), exist_ok=True)
         with open(self.path(), "a") as fa:
            fa.write(samples)
            self.stats(instance, strategy, samples)
      finally:
         self._lock.release()
    
   def stats(self, instance, strategy, samples):
      "Save optional statistics."
      pass

