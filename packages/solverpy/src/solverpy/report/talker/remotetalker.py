"""
# RemoteTalker — cross-process talker proxy

Wraps a local [`Talker`][solverpy.report.talker.talker.Talker] and makes its
lifecycle methods callable from a child process.  Every public method that is
**not** listed in `LOCALS` is intercepted by `__getattribute__` and put on a
queue instead of executing directly; a background listening thread in the parent
dequeues each message and calls the real method on the wrapped local talker.

`LOCALS` names the small set of methods that must execute in the calling
process (queue/thread lifecycle); everything else is forwarded automatically —
no need to enumerate every talker method.

When the `RemoteTalker` is pickled into a spawn worker only the queue is
needed: `_local` is excluded from the pickled state so that UI objects (tqdm
bars, etc.) are not serialised unnecessarily.
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
   abstract class solverpy.report.talker.talker.Talker
   class solverpy.report.talker.remotetalker.RemoteTalker extends solverpy.report.talker.talker.Talker {
      + LOCALS: set[str]
      - _remote_queue: Queue[Any]
      - _listening_thread: Thread | None
      - _local: Talker
      --
      + listening_start()
      + listening_stop()
      + listening_handle(method, args, kwargs)
      + terminate()
   }
   class solverpy.report.talker.logtalker.LogTalker extends solverpy.report.talker.talker.Talker
   class solverpy.report.talker.evaltalker.EvalTalker extends solverpy.report.talker.logtalker.LogTalker
   solverpy.report.talker.remotetalker.RemoteTalker o-- solverpy.report.talker.talker.Talker : wraps
   ```

   Any public attribute **not** listed in `LOCALS` is intercepted by
   `__getattribute__` and replaced with a wrapper that puts
   ``(name, args, kwargs)`` on ``_remote_queue``.  The listening thread in the
   parent picks up each message and calls the real method on ``_local``.

   Methods listed in `LOCALS` execute directly in the calling process (queue
   and thread lifecycle helpers that must not be forwarded).
   """

   LOCALS = {
      "log_start",
      "log_stop",
      "log_config",
      "listening_start",
      "listening_stop",
      "listening_handle",
   }
   """Methods that execute locally in the calling process (not forwarded via queue)."""

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
      if not name.startswith('_') and name not in RemoteTalker.LOCALS:
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
      """Signal the listening thread to stop, drain remaining queue items, then join."""
      if not (self._listening_thread and self._listening_thread.is_alive()):
         super().listening_stop()
         return

      self._stop_listening.set()
      self._listening_thread.join(timeout=2.0)
      self._listening_thread = None

      try:
         while True:
            method, args, kwargs = self._remote_queue.get_nowait()
            self.listening_handle(method, args, kwargs)
      except Exception:
         pass

      super().listening_stop()

   def _listen_loop(self):
      """Drain ``_remote_queue`` and dispatch each message to ``listening_handle``."""
      while not self._stop_listening.is_set():
         try:
            method, args, kwargs = self._remote_queue.get(timeout=0.2)
            self.listening_handle(method, args, kwargs)
         except:
            pass

   def listening_handle(self, method, args, kwargs):
      """Call ``method`` on the local talker with the given args and kwargs."""
      local = object.__getattribute__(self, '_local')
      if local is None:
         return
      handler = None
      try:
         handler = getattr(local, method)
      except AttributeError:
         logger.error(
            f"Method '{method}' not found on local talker\n{local}\n{dir(local)}"
         )
      if not handler:
         return
      try:
         handler(*args, **kwargs)
      except Exception as e:
         logger.error(f"Error calling {method}: {e}", exc_info=True)

   def terminate(self):
      """Terminate the local talker (dispatched from child via queue)."""
      local = object.__getattribute__(self, '_local')
      if local:
         local.terminate()

   def __getstate__(self):
      state = self.__dict__.copy()
      state['_listening_thread'] = None
      state['_stop_listening'] = None
      state['_remote_manager'] = None
      state['_local'] = None  # only the queue is needed in spawn workers
      return state

   def __setstate__(self, state):
      self.__dict__.update(state)
      self._stop_listening = threading.Event()
