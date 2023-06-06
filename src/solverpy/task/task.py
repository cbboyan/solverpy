import logging

logger = logging.getLogger(__name__)

class Task:

   def __init__(self, queue=None):
      self._queue = queue

   def run(self):
      raise NotImplementedError("Task.run: abstract method not implemented.")

   @property
   def queue(self):
      return self._queue

   @queue.setter
   def queue(self, q):
      self._queue = q

   def status(self, result):
      return (result is not None)

   @staticmethod
   def runtask(task):
      try:
         res = task.run()
         status = task.status(res)
      except Exception as e:
         import traceback
         logger.warning(f"Exception:: {e}")
         logger.warning(f"Task:: {task}")
         logger.warning(f"Error:: {traceback.format_exc()}")
         status = None
         res = None
      except KeyboardInterrupt:
         return None
      if status is None:
         logger.debug(f"failed task: {task}")
      task.queue.put(status)
      return res

def runtask(task):
   return task.runtask(task)

def setqueue(queue, tasks):
   for task in tasks:
      task.queue = queue

