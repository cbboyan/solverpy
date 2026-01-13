from typing import Any, Sequence, TYPE_CHECKING
import signal
import logging

if TYPE_CHECKING:
   from queue import Queue
   from ..task.talker import Talker

logger = logging.getLogger(__name__)


class Task:
   """A generic executable task/job.

   Represents a task that can be executed.  The result can be returned or
   communicated over a queue.  The abstract method `run` should run the task
   and return the result.

   Tasks are typically executed in different threads.  Hence modification to
   the Task instance might not be visible to the main thread.  Also the
   returned result should be as small as possible to limit inter-process
   communication.

   Alternatively, the communication queue can be used to send the result to the
   main thread.  If the queue is set, the result is transformed to the `status`
   and this status is pushed onto the queue (see `Task.runtask`).  

   Status is also propagated to the progress bar using the `status` bar handler
   (see `RunningBar.status`).  `DefaultBar` ignores the status.  `RunningBar`
   expects the status for failed tasks to be None, and non-None otherwise.
   `SolvingBar` expects `True` for solved tasks, `False` for unsolved, and
   `None` for failed tasks.
   """

   def __init__(
      self,
      queue: "Queue[Any] | None" = None,
      talker: "Talker | None" = None,
   ):
      """Init the task.

      :param queue: communication queue (optional) 

      """
      self._log_queue = queue
      self._talker = talker

   def run(self) -> Any:
      """Run the task and return the result."""
      raise NotImplementedError("Task.run: abstract method not implemented.")

   @property
   def logqueue(self) -> "Queue[Any] | None":
      """Get the queue."""
      return self._log_queue

   @logqueue.setter
   def logqueue(self, q: "Queue[Any]"):
      """Set the queue.

      :param q: the queue

      """
      self._log_queue = q

   #@property
   #def talker(self) -> "Talker | None":
   #   """Get the talker."""
   #   return self._talker

   #@talker.setter
   #def talker(self, talker: "Talker | None"):
   #   """Set the talker.

   #   :param t: the talker

   #   """
   #   self._talker = talker

   def status(
      self,
      result: Any,
   ) -> Any:
      """Translate the result to (typically smaller) status to send it over the
      queue."

      :param result: the result

      """
      return (result is not None)

   @staticmethod
   def runtask(task: "Task"):
      """Run the task andd announce the result over the queue.

      :param task: the task to be ran

      """
      signal.signal(signal.SIGINT, signal.SIG_IGN)
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
      #except KeyboardInterrupt as e:
      #   raise e
      #   #return None
      if status is None:
         logger.debug(f"failed task: {task}")
      #if task.queue is not None:
      #   task.queue.put(status)
      return res


def runtask_single(task: Task) -> Any:
   """Run task and return the result.

   :param task: 

   """
   return task.runtask(task)


def runtask(task: Task) -> Any:
   """Run task and return the result.

   :param task: 

   """
   return (task, task.runtask(task))


#def setqueue(queue: "Queue[Any]", tasks: Sequence[Task]) -> None:
#   """Set the queue for a list of tasks.
#
#   :param queue: the queue to set
#   :param tasks: the tasks to update
#
#   """
#   for task in tasks:
#      task.queue = queue

