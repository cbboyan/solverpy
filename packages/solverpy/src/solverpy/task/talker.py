"""
class Talker

```plantuml name="task-talker"

class Talker {
  - _log_queue: Queue[Any] | None
  - _listener: QueueListener | None
  
  + __init__()
  + {static} log_config(queue)
  + log_start()
  + log_stop()
  + listening_start()
  + listening_stop()
  + begin(jobs, refjob, sidnames, **kwargs)
  + end(results, refjob)
  + next(job)
  + terminate()
  + launching(tasks)
  + finished(task, result)
  + done()
}

note right of Talker::log_config
  Configure child process logger
  to use the queue
end note

note right of Talker::log_start
  Start parent logging 
  from the queue
end note

note right of Talker::log_stop
  Stop parent logging
  from the queue
end note

note right of Talker::begin
  Abstract method
  Raises NotImplementedError
end note

```

"""

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
      self._listener: QueueListener | None = None
      self._manager: mp.managers.SyncManager | None = None

   @staticmethod
   def log_config(queue: "Queue[Any] | None") -> None:
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

   def log_start(self) -> None:
      """Start parent logging from the queue."""
      root = logging.getLogger()
      self._manager = mp.get_context("spawn").Manager()
      assert self._manager
      self._log_queue = self._manager.Queue()
      assert self._log_queue
      self._listener = QueueListener(self._log_queue, *root.handlers)
      self._listener.start()

   def log_stop(self) -> None:
      """Stop parent logging from the queue."""
      if self._listener:
         self._listener.stop()
         self._listener = None
      if self._manager:
         self._manager.shutdown()
         self._manager = None

   def listening_start(self) -> None:
      self.log_start()

   def listening_stop(self) -> None:
      self.log_stop()

   def begin(
      self,
      jobs: list["SolverJob"],
      *,
      refjob: "SolverJob | None" = None,
      sidnames: bool = True,
      **kwargs,
   ) -> None:
      del jobs, refjob, sidnames, kwargs
      raise NotImplementedError(
         "Talker.begin: abstract method not implemented.")

   def end(
      self,
      results: dict["SolverJob", "Result"],
      refjob: "SolverJob | None" = None,
   ) -> None:
      del results, refjob  # unused arguments
      self.terminate()

   def next(self, job: "SolverJob") -> None:
      del job  # unused arguments
      pass

   def terminate(self) -> None:
      self.log_stop()

   def launching(self, tasks: Sequence["Task"]) -> None:
      if self._log_queue is None:
         return
      for task in tasks:
         task.logqueue = self._log_queue

   def finished(self, task: "SolverTask", result: "Result") -> None:
      del task, result  # unused arguments
      pass

   def done(self) -> None:
      pass
