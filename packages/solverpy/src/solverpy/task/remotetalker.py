"""
# RemoteTalker — cross-process talker proxy

Wraps a local [`Talker`][solverpy.task.talker.Talker] and makes its lifecycle
methods callable from a child process.  Methods listed in `REMOTES` are
intercepted by `__getattribute__` and queued instead of executed directly;
a background listening thread in the parent dequeues them and calls the real
method on the wrapped local talker.

Used by [`autotuner`][solverpy_learn.builder.autotuner] to let the tuner child
process drive a `SolverTalker` that runs (and renders progress bars) entirely
in the parent.
"""

from typing import Any, TYPE_CHECKING
import logging
import multiprocessing
import threading

from .talker import Talker

if TYPE_CHECKING:
   from queue import Queue

logger = logging.getLogger(__name__)


class RemoteTalker(Talker):
   """
   Proxy talker that forwards method calls from a child process to the parent.

   ```plantuml name="task-remotetalker"
   abstract class solverpy.task.talker.Talker
   class solverpy.task.remotetalker.RemoteTalker extends solverpy.task.talker.Talker {
      + REMOTES: set[str]
      - _remote_queue: Queue[Any]
      - _listening_thread: Thread | None
      - _local: Talker
      --
      + listening_start()
      + listening_stop()
      + listening_handle(method, args, kwargs)
      + terminate()
   }
   class solverpy.task.logtalker.LogTalker extends solverpy.task.talker.Talker
   class solverpy.task.solvertalker.SolverTalker extends solverpy.task.logtalker.LogTalker
   solverpy.task.remotetalker.RemoteTalker o-- solverpy.task.talker.Talker : wraps
   ```

   Any attribute named in `REMOTES` is intercepted by `__getattribute__`
   and replaced with a wrapper that puts ``(name, args, kwargs)`` on
   ``_remote_queue``.  The listening thread in the parent picks up each
   message and calls the real method on ``_local``.

   All other attributes (not in `REMOTES`) pass through to `Talker` normally.
   """

   REMOTES = {
      "log_config",
      "log_start",
      "log_stop",
      "begin",
      "end",
      "next",
      "terminate",
      "launching",
      "finished",
      "done",
   }
   """Set of method names that are queued instead of called directly."""

   def __init__(self, local: Talker, queue: "Queue[Any] | None" = None):
      """
      Args:
          local: the real talker whose methods are called in the parent process.
          queue: queue to use for cross-process communication.  If ``None``
              (default), a forkserver Manager queue is created — required when
              the queue must survive pickling into spawn workers.  Pass a plain
              ``multiprocessing.Queue`` when the child is forked and pickling
              is not needed.
      """
      Talker.__init__(self)
      if queue is not None:
         self._remote_queue: Queue[Any] = queue
         self._remote_manager = None
      else:
         self._remote_manager = multiprocessing.get_context("forkserver").Manager()
         self._remote_queue = self._remote_manager.Queue()
      self._listening_thread: threading.Thread | None = None
      self._stop_listening: threading.Event = threading.Event()
      self._local: Talker = local

   def __getattribute__(self, name):
      if name in RemoteTalker.REMOTES:

         def wrapper(*args, **kwargs):
            queue = object.__getattribute__(self, '_remote_queue')
            queue.put((name, args, kwargs))

         return wrapper

      return super().__getattribute__(name)

   def listening_start(self):
      """Start the log queue listener and the ``_remote_queue`` listening thread."""
      super().listening_start()
      if self._listening_thread and self._listening_thread.is_alive():
         logger.warning("Listening thread already running")
         return

      self._stop_listening.clear()
      self._listening_thread = threading.Thread(
         target=self._listen_loop,
         daemon=True,
      )
      self._listening_thread.start()

   def listening_stop(self):
      """Signal the listening thread to stop and wait for it to join."""
      super().listening_stop()
      if not (self._listening_thread and self._listening_thread.is_alive()):
         logger.warning("No listening thread to stop")
         return

      self._stop_listening.set()
      self._listening_thread.join(timeout=2.0)
      self._listening_thread = None

   def _listen_loop(self):
      """Drain ``_remote_queue`` and dispatch each message to ``listening_handle``."""
      while not self._stop_listening.is_set():
         try:
            # Block until item arrives or timeout
            method, args, kwargs = self._remote_queue.get(timeout=0.2)
            self.listening_handle(method, args, kwargs)
         except:
            # Timeout occurred, check stop flag and loop again
            pass

   def listening_handle(self, method, args, kwargs):
      """Call ``method`` on the local talker with the given args and kwargs."""
      assert method in RemoteTalker.REMOTES
      handler = None
      try:
         handler = getattr(self._local, method)
      except AttributeError:
         logger.error(
            f"Method '{method}' not found on local talker\n{self._local}\n{dir(self._local)}"
         )
      assert handler
      try:
         handler(*args, **kwargs)
      except Exception as e:
         logger.error(f"Error calling {method}: {e}", exc_info=True)

   def __getstate__(self):
      state = self.__dict__.copy()
      state['_listening_thread'] = None
      state['_stop_listening'] = None
      state['_remote_manager'] = None
      return state

   def __setstate__(self, state):
      self.__dict__.update(state)
      self._stop_listening = threading.Event()

   def terminate(self):
      """Terminate the local talker, stop the listening thread, and shut down the Manager."""
      super().terminate()
      self._local.terminate()
      if self._listening_thread and self._listening_thread.is_alive():
         self._stop_listening.set()
         self._listening_thread.join(timeout=2.0)
         self._listening_thread = None
      if self._remote_manager:
         self._remote_manager.shutdown()
         self._remote_manager = None
