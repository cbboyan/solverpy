from typing import Any, TextIO, TYPE_CHECKING
import os, json
import logging

from ..cachedprovider import CachedProvider
from ...path import bids, sids

if TYPE_CHECKING:
   from ....task.solvertask import SolverTask

logger = logging.getLogger(__name__)

NAME = "results"


class Jsons(CachedProvider):

   def __init__(
      self,
      bid: str,
      sid: str,
      limit: (str | None) = None,  # TODO: make just `str` here?
      caching: bool = False,
   ):
      CachedProvider.__init__(
         self,
         bid,
         sid,
         limit,
         caching,
         compress=True,
      )

   def query(
      self,
      task: "SolverTask",
   ) -> (dict[str, Any] | None):
      if task.problem in self.cache:
         result = self.cache[task.problem]
         return task.solver.determine(result)
      return None

   def store(
      self,
      task: "SolverTask",
      result: dict[str, Any],
   ) -> None:
      if task.solver.valid(result):
         self.cache[task.problem] = result
         self._uptodate = False

   def cachepath(self):
      return os.path.join(
         bids.dbpath(NAME),
         bids.name(self.bid, limit=self.limittype()),
         sids.name(self.sid),
      ).rstrip("/") + ".json"

   def cacheload(self, fr: TextIO) -> None:
      self.cache = json.load(fr)

   def cachedump(self, fw: TextIO) -> None:
      json.dump(self.cache, fw, indent=3, sort_keys=True)

   def limittype(self) -> str:
      if self.limit is None:
         return "unlimited"
      return "".join(sorted(x[0] for x in self.limit.split("-")))


# TODO: refactor and remove, use Maker instead
class JsonsStore(Jsons):

   def __init__(
      self,
      bid: str,
      sid: str,
      limit: (str | None) = None,
   ):
      Jsons.__init__(
         self,
         bid,
         sid,
         limit,
         caching=True,
      )

