from typing import Any, TYPE_CHECKING, Sequence
import logging
import multiprocessing as mp

from .task import runtask, runtask_single
from .logtalker import LogTalker

if TYPE_CHECKING:
   from .task import Task
   from .talker import Talker

logger = logging.getLogger(__name__)

WAIT = 365 * 24 * 60 * 60  # a year


def run(
   tasks: list["Task"],
   cores: int = 4,
   chunksize: int = 1,
) -> Any:
   """Launch `tasks` in parallel on multiple cores and return results.

   :param tasks:  list of task to be executed (instances of Task)
   :param cores:  number of worker threads (Default value = 4)
   :param chunksize:  chunksize for Pool.map_async (Default value = 1)
   """
   pool = mp.get_context("spawn").Pool(cores)
   try:
      runner = pool.map_async(runtask_single, tasks, chunksize=chunksize)
      results = runner.get(WAIT)
      pool.close()
      pool.join()
      return results
   except (Exception, KeyboardInterrupt):
      pool.terminate()
      raise 


def launch(
   tasks: Sequence["Task"],
   talker: "Talker | None" = None,
   cores: int = 4,
   chunksize: int = 1,
   **others: Any,
) -> Any:
   del others  # unused argument
   talker = talker or LogTalker()
   ret = {}
   logger.debug(f"launching pool with {cores} workers for {len(tasks)} tasks")
   pool = mp.get_context("spawn").Pool(cores)
   tids = {}
   for (n,task) in enumerate(tasks):
      task.tid = n
      tids[n] = task
   talker.launching(tasks)
   try:
      # TODO: eliminate runtask and make it runtask2
      results = pool.imap_unordered(
         runtask,
         tasks,
         chunksize=chunksize,
      )
      count = 0
      logger.debug("pool started")
      for (tid, result) in results:
         talker.finished(tids[tid], result)
         ret[tid] = result
         count += 1
      logger.debug(f"all tasks done: {len(tasks)} total")
      pool.close()
   except KeyboardInterrupt:
      logger.debug("pool terminated (keyboard interupt)")
      pool.terminate()
      talker.terminate()
      #sys.exit(0)
      raise
   finally:
      logger.debug(f"pool join")
      pool.join()
      logger.debug(f"pool closed")
      talker.done()
   return [ret[task.tid] for task in tasks]  # TODO: make it return ret directly
