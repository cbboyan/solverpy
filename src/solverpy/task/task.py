from typing import Any, Sequence, TYPE_CHECKING
import logging

if TYPE_CHECKING:
   from queue import Queue

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
   ):
      """Init the task.

      :param queue: communication queue (optional) 

      """
      self._queue = queue

   def run(self) -> Any:
      """Run the task and return the result."""
      raise NotImplementedError("Task.run: abstract method not implemented.")

   @property
   def queue(self):
      """Get the queue."""
      return self._queue

   @queue.setter
   def queue(self, q: "Queue[Any]"):
      """Set the queue.

      :param q: the queue

      """
      self._queue = q

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
      if task.queue is not None:
         task.queue.put(status)
      return res


def runtask(task: Task) -> Any:
   """Run task and return the result.

   :param task: 

   """
   return task.runtask(task)


def setqueue(queue: "Queue[Any]", tasks: Sequence[Task]) -> None:
   """Set the queue for a list of tasks.

   :param queue: the queue to set
   :param tasks: the tasks to update

   """
   for task in tasks:
      task.queue = queue

