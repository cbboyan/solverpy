from typing import Any, Sequence, TYPE_CHECKING
import logging
import multiprocessing as mp
from queue import Queue
from logging.handlers import QueueHandler, QueueListener

from ..task.task import Task

if TYPE_CHECKING:
   from ..tools.typing import Result, SolverJob
   from ..task.solvertask import SolverTask  # TODO: generalize to Task

logger = logging.getLogger(__name__)


class Talker:

   def __init__(self):
      self._log_queue: Queue[Any] | None = None

   @staticmethod
   def log_config(queue):
      """Configure child process logger to use the queue."""
      if not queue:
         return
      logger.debug("redirecting logger to the queue")
      root = logging.getLogger()
      root.handlers.clear()
      for name in logging.root.manager.loggerDict:
         logging.getLogger(name).handlers.clear()
      root.addHandler(QueueHandler(queue))
      root.setLevel(logging.INFO)
      logger.debug("logging redirected")

   def log_start(self):
      """Start parent logging from the queue."""
      root = logging.getLogger()
      self._log_queue = mp.get_context("spawn").Manager().Queue()
      self._listener = QueueListener(self._log_queue, *root.handlers)
      self._listener.start()

   def log_stop(self):
      """Stop parent logging from the queue."""
      if self._listener:
         self._listener.stop()
         self._listener = None
         #logging.getLogger().handlers = self._handlers.copy()

   def listening_start(self):
      self.log_start()

   def listening_stop(self):
      self.log_stop()

   #def begin(self, total: int, *, desc: str, **kwargs):
   #   del total, desc, kwargs  # unused arguments
   #   raise NotImplementedError(
   #      "Talker.begin: abstract method not implemented.")

   def begin(
      self,
      jobs: list["SolverJob"],
      *,
      refjob: "SolverJob | None" = None,
      sidnames: bool = True,
      **kwargs,
   ):
      del jobs, refjob, sidnames, kwargs
      raise NotImplementedError(
         "Talker.begin: abstract method not implemented.")

   def end(
      self,
      results: dict["SolverJob", "Result"],
      refjob: "SolverJob | None" = None,
   ):
      del results, refjob  # unused arguments
      self.terminate()

   def next(self, job: "SolverJob"):
      del job  # unused arguments
      pass

   def terminate(self):
      pass

   def launching(self, tasks: Sequence["Task"]):
      if self._log_queue is None:
         return
      for task in tasks:
         task.logqueue = self._log_queue

   def finished(self, task: "SolverTask", result: "Result"):
      del task, result  # unused arguments
      pass

   def done(self):
      pass
