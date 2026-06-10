import queue
import threading

from solverpy.report.talker import talker as talker_module
from solverpy.report.talker.remotetalker import RemoteTalker
from solverpy.report.talker.talker import Talker


class FakeManager:

   def __init__(self):
      self.queue = object()
      self.stopped = False

   def Queue(self):
      return self.queue

   def shutdown(self):
      self.stopped = True


class FakeContext:

   def __init__(self, manager):
      self.manager = manager

   def Manager(self):
      return self.manager


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


def test_log_prepare_does_not_start_listener(monkeypatch):
   manager = FakeManager()
   monkeypatch.setattr(
      talker_module.mp,
      "get_context",
      lambda method: FakeContext(manager),
   )
   monkeypatch.setattr(talker_module, "QueueListener", FakeListener)
   talker = Talker()

   talker.log_prepare()

   assert talker._log_queue is manager.queue
   assert talker._listener is None

   talker.log_start()
   listener = talker._listener
   talker.log_start()

   assert listener is talker._listener
   assert listener.started
   assert listener.kwargs == {"respect_handler_level": True}

   talker.log_stop()

   assert listener.stopped
   assert manager.stopped
   assert talker._log_queue is None


def test_log_stop_cleans_prepared_queue(monkeypatch):
   manager = FakeManager()
   monkeypatch.setattr(
      talker_module.mp,
      "get_context",
      lambda method: FakeContext(manager),
   )
   talker = Talker()

   talker.log_prepare()
   talker.log_stop()

   assert manager.stopped
   assert talker._log_queue is None
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
