from typing import Any
import os
import random
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

   def exists(self) -> bool:
      return svm.exists(self.path())

   def stats(
      self,
      instance: tuple[str, str],
      strategy: str,
      samples: str,
   ) -> None:
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
      else:
         logger.warning(f"No trains to compress: {self.path()}.")

   def merge(
      self,
      previous: str | tuple[str, ...],
      outfilename: str,
   ) -> None:
      assert self._filename != outfilename
      assert type(previous) is str
      if not svm.exists(self.path()):
         logger.warning(f"Trains not found: {self.path()}.")
         return
      f_out = self.path(filename=outfilename)
      svm.merge(previous, self.path(), f_out=f_out)
      #self.reset(filename=outfilename)

   def link(self, src: str | tuple[str]):
      assert isinstance(src, str)
      if not svm.exists(src):
         logger.warning(f"Link source not found: {src}.")
         return
      dst = self.path()
      if svm.exists(dst):
         logger.warning(f"Link targed exists: {dst}.")
         return
      svm.link(src, dst)


def filter_posneg(
   samples: list[Any],
   ratio: float,
   seed: int = 0,
) -> list[Any]:
   if ratio == 0:
      return samples
   pos = [x for x in samples if x.startswith("1")]
   neg = [x for x in samples if x.startswith("0")]
   random.seed(seed)
   if (ratio > 0) and (len(pos) * ratio < len(neg)):
      # filter negative samples
      neg = random.sample(neg, int(len(pos) * ratio))
      samples = pos + neg
   if (ratio < 0) and (len(neg) * -ratio < len(pos)):
      # filter positive samples
      pos = random.sample(pos, int(len(neg) * -ratio))
      samples = pos + neg
   return samples
