from types import SimpleNamespace

import pytest

from solverpy.report.talker.talker import Talker
from solverpy.setups import runtime as runtime_mod
from solverpy_learn.builder.plugins.enigma import EnigmaMultiTrains
from solverpy_learn.builder.plugins.svm import SvmTrains
from solverpy_learn import setups
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


def test_eprover_configures_independent_evalset_solvers():
   setup = setups.Setup(
      options=["headless"],
      sel_features="features",
      trains=setups.Evalset(dataname="train"),
      devels=setups.Evalset(dataname="devel"),
   )

   setups.experiment(setup)
   setups.eprover(setup)

   trains = setup["trains"]
   devels = setup["devels"]
   assert "solver" not in setup
   assert trains["solver"] is not devels["solver"]
   assert trains["plugin"] is not devels["plugin"]
   assert trains["plugin"] in trains["solver"].decorators
   assert trains["plugin"] not in devels["solver"].decorators
   assert devels["plugin"] in devels["solver"].decorators
   assert devels["plugin"] not in trains["solver"].decorators


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


def test_launch_prepares_both_evalsets_then_builds_once(monkeypatch):
   events = []

   class FakePlugin:

      def __init__(self, dataname):
         self.dataname = dataname

      def path(self):
         return f"{self.dataname}/train.in"

      def reset(self, dataname=None, filename="train.in"):
         del filename
         if dataname is not None:
            self.dataname = dataname

   class FakeBuilder:

      strategies = ["new"]

      def reset(self, dataname):
         events.append(("reset", dataname))

      def build(self, talker):
         del talker
         events.append(("build",))

   runtime = SimpleNamespace(shutdown=lambda: None)
   talker = SimpleNamespace(log_stop=lambda: None)
   setup = {
      "options": [],
      "loops": 1,
      "trains": {
         "dataname": "train",
         "plugin": FakePlugin("train"),
         "strategies": ["sid"],
      },
      "devels": {
         "dataname": "devel",
         "plugin": FakePlugin("devel"),
         "strategies": ["sid"],
      },
      "builder": FakeBuilder(),
      "talker": talker,
   }

   monkeypatch.setattr(loop, "boot", lambda setup: runtime)
   monkeypatch.setattr(
      loop,
      "oneloop",
      lambda setup, evalset: events.append(("prepare", evalset["label"])),
   )
   monkeypatch.setattr(loop.evaluator, "init", lambda setup: None)
   monkeypatch.setattr(loop.log, "ntfy", lambda *args, **kwargs: None)
   monkeypatch.setattr(loop, "resource_summary", lambda *args: "")
   monkeypatch.setattr(loop, "usage", lambda *args: "")

   loop.launch(setup)

   assert events == [
      ("reset", "train/loop00"),
      ("prepare", "development"),
      ("prepare", "training"),
      ("build",),
      ("reset", "train/loop01"),
      ("prepare", "development"),
   ]
   assert setup["trains"]["strategies"] == ["sid", "new"]
   assert setup["devels"]["strategies"] == ["sid", "new"]


def test_launch_keeps_previous_trains_from_prior_loop(monkeypatch):
   class FakePlugin:

      def __init__(self):
         self._dataname = "train"
         self._filename = "train.in"

      def reset(self, dataname=None, filename="train.in"):
         if dataname is not None:
            self._dataname = dataname
         self._filename = filename

      def path(self):
         return f"{self._dataname}/{self._filename}"

   runtime = SimpleNamespace()
   runtime.shutdown = lambda: None
   runtime.log_queue = SimpleNamespace()
   talker = SimpleNamespace(log_start=lambda: None, log_stop=lambda: None)
   evalset = {
      "dataname": "train",
      "basedataname": "train",
      "label": "training",
      "plugin": FakePlugin(),
      "strategies": ["sid"],
      "refs": ["sid"],
   }
   setup = {
      "options": [],
      "loops": 1,
      "trains": evalset,
      "talker": talker,
   }

   monkeypatch.setattr(loop, "boot", lambda setup: runtime)
   monkeypatch.setattr(loop, "oneloop", lambda setup, evalset: evalset)
   monkeypatch.setattr(loop.evaluator, "init", lambda setup: None)
   monkeypatch.setattr(loop.log, "ntfy", lambda *args, **kwargs: None)
   monkeypatch.setattr(loop, "resource_summary", lambda *args: "")
   monkeypatch.setattr(loop, "usage", lambda *args: "")

   loop.launch(setup)

   assert evalset["previous_trains"] == "train/loop00/train.in"
