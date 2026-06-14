from types import SimpleNamespace

import pytest

from solverpy.report.talker.talker import Talker
from solverpy.setups import runtime as runtime_mod
from solverpy_learn.builder.plugins.enigma import EnigmaMultiTrains
from solverpy_learn.builder.plugins.svm import SvmTrains
from solverpy_learn.setups import loop


class FakeLock:
   pass


class FakeManager:

   def __init__(self):
      self.locks = []
      self.namespaces = []
      self.stopped = False

   def Queue(self):
      return SimpleNamespace()

   def Lock(self):
      lock = FakeLock()
      self.locks.append(lock)
      return lock

   def Namespace(self):
      namespace = SimpleNamespace()
      self.namespaces.append(namespace)
      return namespace

   def shutdown(self):
      self.stopped = True


class FakeContext:

   def __init__(self):
      self.managers = []

   def Manager(self):
      manager = FakeManager()
      self.managers.append(manager)
      return manager


def test_trains_defer_shared_state_until_initialize(monkeypatch):
   context = FakeContext()
   monkeypatch.setattr(runtime_mod.multiprocessing, "get_context", lambda method: context)

   train = SvmTrains("train")
   devel = SvmTrains("devel")

   assert context.managers == []
   assert train._lock is None
   assert devel._lock is None

   runtime = loop.initialize({"plugins": [train, devel]})
   manager = context.managers[0]

   assert len(context.managers) == 1
   assert len(manager.locks) == 2
   assert len(manager.namespaces) == 2
   assert train._lock is manager.locks[0]
   assert devel._lock is manager.locks[1]

   train.info.total = 7
   runtime.shutdown()

   assert manager.stopped
   assert train._lock is None
   assert devel._lock is None
   assert train.info.total == 7


def test_runtime_allows_reinitialization(monkeypatch):
   context = FakeContext()
   monkeypatch.setattr(runtime_mod.multiprocessing, "get_context", lambda method: context)
   trains = SvmTrains("train")
   setup = {"plugins": [trains]}

   first = loop.initialize(setup)
   first.shutdown()
   second = loop.initialize(setup)
   second.shutdown()

   assert len(context.managers) == 2
   assert all(manager.stopped for manager in context.managers)


def test_multi_trains_share_session_manager(monkeypatch):
   context = FakeContext()
   monkeypatch.setattr(runtime_mod.multiprocessing, "get_context", lambda method: context)
   train = EnigmaMultiTrains("train", "sel-features", "gen-features")
   devel = EnigmaMultiTrains("devel", "sel-features", "gen-features")

   runtime = loop.initialize({"plugins": [train, devel]})
   manager = context.managers[0]

   assert len(context.managers) == 1
   assert len(manager.locks) == 4
   assert len(manager.namespaces) == 4

   runtime.shutdown()
   assert manager.stopped


def test_launch_shuts_runtime_down_on_failure(monkeypatch):
   runtime = SimpleNamespace(stopped=False)
   runtime.shutdown = lambda: setattr(runtime, "stopped", True)
   messages = []

   def fake_boot(setup):
      setup["talker"] = Talker()
      return runtime

   monkeypatch.setattr(loop, "boot", fake_boot)
   monkeypatch.setattr(loop.log, "ntfy", lambda *args, **kwargs: None)
   monkeypatch.setattr(loop, "usage", lambda label: label)
   monkeypatch.setattr(
      loop.logger,
      "debug",
      lambda message: messages.append((message, runtime.stopped)),
   )

   def fail(*args, **kwargs):
      raise RuntimeError("evaluation initialization failed")

   monkeypatch.setattr(loop.evaluator, "init", fail)

   with pytest.raises(RuntimeError, match="evaluation initialization failed"):
      loop.launch({})

   assert runtime.stopped
   assert messages == [
      ("run start: unknown", False),
      ("run end: unknown", True),
   ]
