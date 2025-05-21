from typing import Any, TYPE_CHECKING
import logging

if TYPE_CHECKING:
   from .task import Task
   from .solvertask import SolverTask
   from .bar import DefaultBar

from multiprocessing import Pool, Manager
from .task import runtask, setqueue
from .bar import DefaultBar

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
      runner = pool.map_async(runtask, tasks, chunksize=chunksize)
      results = runner.get(WAIT)
      pool.close()
      pool.join()
      return results
   except (Exception, KeyboardInterrupt) as e:
      pool.terminate()
      raise e


def launch(
   tasks: list[SolverTask],
   cores: int = 4,
   chunksize: int = 1,
   taskdone: Any = None,
   bar: "DefaultBar | None" = None,
   desc: str = "running",
   **others: Any,
) -> Any:
   """Launch `tasks` in parallel on multiple cores, communicate status over the
   queue, and show progress bar.
   
   :param tasks:  list of task to be executed (instances of Task)
   :param cores:  number of worker threads (Default value = 4)
   :param chunksize:  chunksize for Pool.map_async (Default value = 1)
   :param taskdone:  (Default value = None)
   :param bar:  (Default value = None)
   :param desc:  (Default value = "running")
   :param **others: 
   """
   del others # unused argument
   todo = len(tasks)
   pool = Pool(cores)
   m = Manager()
   queue = m.Queue()
   setqueue(queue, tasks)
   bar = bar or DefaultBar(len(tasks), desc, miniters=1)
   logger.debug(f"launching pool with {cores} workers for {todo} tasks")
   try:
      runner = pool.map_async(runtask, tasks, chunksize=chunksize)
      while todo:
         status = queue.get(WAIT) # type: ignore
         bar.status(status)
         if taskdone:
            taskdone(status)
         todo -= 1
      bar.close()
      logger.debug(f"all tasks done")
      pool.close()
      pool.join()
      logger.debug(f"pool closed")
      return runner.get(WAIT)
   except KeyboardInterrupt as e:
      bar.close()
      logger.debug("pool terminated (keyboard interupt)")
      pool.terminate()
      raise e
