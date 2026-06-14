import queue
import threading

from solverpy.report.talker import talker as talker_module
from solverpy.report.talker.remotetalker import RemoteTalker
from solverpy.report.talker.talker import Talker


class FakeListener:

   def __init__(self, queue, *handlers, **kwargs):
      self.queue = queue
      self.handlers = handlers
      self.kwargs = kwargs
      self.started = False
      self.stopped = False

   def start(self):
      self.started = True

   def stop(self):
      self.stopped = True


def test_log_start_starts_listener_when_queue_set(monkeypatch):
   monkeypatch.setattr(talker_module, "QueueListener", FakeListener)
   fake_queue = object()
   talker = Talker()
   talker._log_queue = fake_queue

   talker.log_start()
   listener = talker._listener
   talker.log_start()   # second call is a no-op

   assert listener is talker._listener
   assert listener.started
   assert listener.kwargs == {"respect_handler_level": True}


def test_log_start_noop_without_queue():
   talker = Talker()
   talker.log_start()   # _log_queue is None → no-op
   assert talker._listener is None


def test_log_stop_stops_listener(monkeypatch):
   monkeypatch.setattr(talker_module, "QueueListener", FakeListener)
   talker = Talker()
   talker._log_queue = object()
   talker.log_start()
   listener = talker._listener

   talker.log_stop()

   assert listener.stopped
   assert talker._log_queue is not None  # queue is not cleared; Runtime owns its lifecycle
   assert talker._listener is None


def test_remote_talker_delivers_event_queued_before_listener_start(monkeypatch):
   received = threading.Event()

   class RecordingTalker(Talker):

      def info(self, msg):
         if msg == "early":
            received.set()

   monkeypatch.setattr(Talker, "log_start", lambda self: None)
   monkeypatch.setattr(Talker, "log_stop", lambda self: None)
   remote = RemoteTalker(RecordingTalker(), queue=queue.Queue())

   remote.info("early")
   remote.listening_start()

   assert received.wait(timeout=1.0)
   remote.listening_stop()
