from typing import Any, TYPE_CHECKING, Sequence
import sys
import logging

if TYPE_CHECKING:
   from .task import Task
   #from .bar import DefaultBar
   from .talker import Talker

from multiprocessing import Pool #, Manager
from .task import runtask, runtask_single
#from .bar import DefaultBar
from .logtalker import LogTalker

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
   pool = Pool(cores)
   try:
      runner = pool.map_async(runtask_single, tasks, chunksize=chunksize)
      results = runner.get(WAIT)
      pool.close()
      pool.join()
      return results
   except (Exception, KeyboardInterrupt):
      pool.terminate()
      raise 


#def launch(
#   tasks: Sequence["Task"],
#   cores: int = 4,
#   chunksize: int = 1,
#   taskdone: Any = None,
#   bar: "DefaultBar | None" = None,
#   desc: str = "running",
#   **others: Any,
#) -> Any:
#   """Launch `tasks` in parallel on multiple cores, communicate status over the
#   queue, and show progress bar.
#
#   :param tasks:  list of task to be executed (instances of Task)
#   :param cores:  number of worker threads (Default value = 4)
#   :param chunksize:  chunksize for Pool.map_async (Default value = 1)
#   :param taskdone:  (Default value = None)
#   :param bar:  (Default value = None)
#   :param desc:  (Default value = "running")
#   :param **others:
#   """
#   del others  # unused argument
#   todo = len(tasks)
#   pool = Pool(cores)
#   m = Manager()
#   queue = m.Queue()
#   setqueue(queue, tasks)
#   bar = bar or DefaultBar(len(tasks), desc, miniters=1)
#   logger.debug(f"launching pool with {cores} workers for {todo} tasks")
#   try:
#      runner = pool.map_async(runtask, tasks, chunksize=chunksize)
#      while todo:
#         status = queue.get(WAIT)  # type: ignore
#         bar.status(status)
#         if taskdone:
#            taskdone(status)
#         todo -= 1
#      bar.close()
#      logger.debug(f"all tasks done")
#      pool.close()
#      pool.join()
#      logger.debug(f"pool closed")
#      return runner.get(WAIT)
#   except KeyboardInterrupt as e:
#      bar.close()
#      logger.debug("pool terminated (keyboard interupt)")
#      pool.terminate()
#      raise e


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
   pool = Pool(cores)
   talker.launching(tasks)
   try:
      # TODO: eliminate runtask and make it runtask2
      results = pool.imap_unordered(
         runtask,
         tasks,
         chunksize=chunksize,
      )
      count = 0
      for (task, result) in results:
         talker.finished(task, result)
         ret[task] = result
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
   return [ret[task] for task in tasks]  # TODO: make it return ret directly
