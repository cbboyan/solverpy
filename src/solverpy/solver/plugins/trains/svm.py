import os
import logging
import multiprocessing

from ..decorator import Decorator
from ....benchmark.path import bids
from ....trains import svm

from .trains import Trains

logger = logging.getLogger(__name__)

class SvmTrains(Trains):

   def __init__(self, dataname, filename="train.in"):
      Trains.__init__(self, dataname, filename=filename)
      self.info = multiprocessing.Manager().Namespace()
      self.info.total = 0
      self.info.pos = 0
      self.info.neg = 0
   
   def stats(self, instance, strategy, samples):
      count = samples.count("\n")
      s0 = samples[0]
      pos = samples.count("\n1 ") + (1 if s0 == "1" else 0)
      neg = samples.count("\n0 ") + (1 if s0 == "0" else 0)
      self.info.total += count
      self.info.pos += pos
      self.info.neg += neg
      with open(self.file+"-stats.txt", "a") as infa:
         infa.write(f"{instance} {strategy}: {count} ({pos} / {neg})\n")

   def compress(self):
      logger.info(f"Training vectors count: {self.info.total} ({self.info.pos} / {self.info.neg}) ")
      svm.compress(self.file)
        
