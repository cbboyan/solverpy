import os
import logging
import multiprocessing

from .. import svm
from .trains import Trains

logger = logging.getLogger(__name__)


class SvmTrains(Trains):

   def __init__(self, dataname: str, filename: str = "train.in"):
      Trains.__init__(self, dataname, filename=filename)
      self.info = multiprocessing.Manager().Namespace()
      self.info.total = 0
      self.info.pos = 0
      self.info.neg = 0

   def stats(self, instance: tuple[str, str], strategy: str,
             samples: str) -> None:
      count = samples.count("\n")
      s0 = samples[0]
      pos = samples.count("\n1 ") + (1 if s0 == "1" else 0)
      neg = samples.count("\n0 ") + (1 if s0 == "0" else 0)
      self.info.total += count
      self.info.pos += pos
      self.info.neg += neg
      with open(self.path() + "-stats.txt", "a") as infa:
         infa.write(f"{instance} {strategy}: {count} ({pos} / {neg})\n")

   def compress(self) -> None:
      logger.info(
         f"Training vectors count: {self.info.total} ({self.info.pos} / {self.info.neg}) "
      )
      if os.path.isfile(self.path()):
         svm.compress(self.path())

   def merge(
      self,
      previous: str | tuple[str, ...],
      outfilename: str,
   ) -> None:
      assert self._filename != outfilename
      assert type(previous) is str
      f_out = self.path(filename=outfilename)
      svm.merge(previous, self.path(), f_out=f_out)
      #self.reset(filename=outfilename)
