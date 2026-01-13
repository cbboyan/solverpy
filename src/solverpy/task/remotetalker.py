import logging
import multiprocessing
import threading

from .talker import Talker

logger = logging.getLogger(__name__)


class RemoteTalker(Talker):

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

   def __init__(self, local: Talker):
      Talker.__init__(self)
      manager = multiprocessing.Manager()
      self._remote_queue = manager.Queue()
      self._listening_thread = None
      self._stop_listening = threading.Event()
      self._local = local

   def __getattribute__(self, name):
      if name in RemoteTalker.REMOTES:

         def wrapper(*args, **kwargs):
            queue = object.__getattribute__(self, '_remote_queue')
            queue.put((name, args, kwargs))

         return wrapper

      return super().__getattribute__(name)

   def listening_start(self):
      """Start listening thread (non-blocking)."""
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
      """Stop the listening thread."""
      super().listening_stop()
      if not (self._listening_thread and self._listening_thread.is_alive()):
         logger.warning("No listening thread to stop")
         return

      self._stop_listening.set()
      self._listening_thread.join(timeout=2.0)
      self._listening_thread = None

   def _listen_loop(self):
      """Internal method that runs in the listening thread."""
      while not self._stop_listening.is_set():
         try:
            # Block until item arrives or timeout
            method, args, kwargs = self._remote_queue.get(timeout=0.2)
            self.listening_handle(method, args, kwargs)
         except:
            # Timeout occurred, check stop flag and loop again
            pass

   def listening_handle(self, method, args, kwargs):
      """Handle received method calls by delegating to local talker."""
      assert method in RemoteTalker.REMOTES
      handler = None
      try:
         handler = getattr(self._local, method)
      except AttributeError:
         logger.error(f"Method '{method}' not found on local talker\n{self._local}\n{dir(self._local)}")
      assert handler
      try:
         handler(*args, **kwargs)
      except Exception as e:
         logger.error(f"Error calling {method}: {e}", exc_info=True)
