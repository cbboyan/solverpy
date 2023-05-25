import logging

from multiprocessing import Pool, Manager
from .task import runtask, setqueue
from .bar import DefaultBar

logger = logging.getLogger(__name__)

WAIT = 365*24*60*60 # a year

def run(tasks, cores=4, chunksize=1):
   pool = Pool(cores)
   try:
      runner = pool.map_async(runtask, tasks, chunksize=chunksize)
      results = runner.get(WAIT)
      pool.close()
      pool.join()
      return results
   except KeyboardInterrupt as e:
      pool.terminate()
      raise e

def launch(tasks, cores=4, chunksize=1, taskdone=None, bar=None, desc="running", **others):
   todo = len(tasks)
   pool = Pool(cores)
   m = Manager()
   queue = m.Queue()
   setqueue(queue, tasks)
   bar = bar if bar else DefaultBar(len(tasks), desc)
   logger.debug(f"launching pool with {cores} workers for {todo} tasks")
   try:
      runner = pool.map_async(runtask, tasks, chunksize=chunksize)
      while todo:
         status = queue.get(WAIT)
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

