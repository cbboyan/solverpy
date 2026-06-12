import signal
from types import SimpleNamespace

import pytest

from solverpy_learn.builder.autotune import autotune


class FakeProcess:

   def __init__(self, pid=123, alive=True):
      self.pid = pid
      self.alive = alive
      self.joins = []
      self.terminated = False
      self.killed = False

   def is_alive(self):
      return self.alive

   def join(self, timeout=None):
      self.joins.append(timeout)
      if timeout is None:
         self.alive = False

   def terminate(self):
      self.terminated = True

   def kill(self):
      self.killed = True


def test_tuner_process_starts_new_session(monkeypatch):
   calls = []
   monkeypatch.setattr(autotune.os, "setsid", lambda: calls.append("setsid"))
   monkeypatch.setattr(
      autotune.redirect,
      "call",
      lambda *args, **kwargs: calls.append((args, kwargs)),
   )

   autotune._tuner_process("arg", key="value")

   assert calls == ["setsid", (("arg", ), {"key": "value"})]


def test_terminate_tuner_kills_process_group(monkeypatch):
   process = FakeProcess()
   signals = []
   monkeypatch.setattr(autotune.os, "getpgid", lambda pid: pid)
   monkeypatch.setattr(
      autotune.os,
      "killpg",
      lambda pid, sig: signals.append((pid, sig)),
   )

   autotune._terminate_tuner(process)

   assert signals == [
      (process.pid, signal.SIGTERM),
      (process.pid, signal.SIGKILL),
   ]
   assert process.joins == [autotune.TERMINATE_TIMEOUT, None]
   assert not process.terminated
   assert not process.killed


def test_terminate_tuner_falls_back_before_setsid(monkeypatch):
   process = FakeProcess()
   monkeypatch.setattr(autotune.os, "getpgid", lambda pid: pid - 1)

   autotune._terminate_tuner(process)

   assert process.terminated
   assert process.killed
   assert process.joins == [autotune.TERMINATE_TIMEOUT, None]


def test_terminate_tuner_ignores_unstarted_process():
   process = SimpleNamespace(pid=None)

   autotune._terminate_tuner(process)


def test_tuner_prefixes_repeated_phase_names(monkeypatch, tmp_path):
   calls = []

   class FakeTalker:
      _log_queue = None

      def __getattr__(self, name):
         del name
         return lambda *args, **kwargs: None

   def phase(**kwargs):
      calls.append(kwargs["nick"])
      return ((0, None, None, None, None), {})

   monkeypatch.setattr(autotune, "_datasets",
                       lambda *args, **kwargs: (object(), object(), 1, 2))
   monkeypatch.setattr(
      autotune,
      "PHASES",
      {
         "l": phase,
         "w": phase,
      },
   )

   autotune.tuner(
      "train",
      "test",
      d_tmp=str(tmp_path),
      phases="l:w:l",
      iters=15,
      talker=FakeTalker(),
   )

   assert calls == ["01-leaves", "02-posneg", "03-leaves"]


def test_prettytuner_starts_process_before_listeners(monkeypatch, tmp_path):
   calls = []

   class LocalTalker:

      def __init__(self):
         self._log_queue = None
         self._result = "result"

      def terminate(self):
         calls.append("talker terminate")

   class FakeRemote:

      def __init__(self, local, queue):
         del local, queue
         self._log_queue = None

      def log_prepare(self):
         calls.append("log prepare")
         self._log_queue = "log queue"

      def listening_start(self):
         calls.append("listeners start")

      def listening_stop(self):
         calls.append("listeners stop")

   class TuneProcess:
      pid = 123

      def start(self):
         calls.append("process start")

      def join(self):
         calls.append("process join")

   class FakeContext:

      def Process(self, **kwargs):
         calls.append("process create")
         assert kwargs["target"] is autotune._tuner_process
         assert kwargs["kwargs"]["talker"]._log_queue is None
         return TuneProcess()

   monkeypatch.setattr(autotune, "RemoteTalker", FakeRemote)
   monkeypatch.setattr(autotune.multiprocessing, "Queue", lambda: object())
   monkeypatch.setattr(
      autotune.multiprocessing,
      "get_context",
      lambda method: FakeContext(),
   )
   talker = LocalTalker()

   result = autotune.prettytuner(talker=talker, d_tmp=str(tmp_path))

   assert result == "result"
   assert calls == [
      "process create",
      "log prepare",
      "process start",
      "listeners start",
      "process join",
      "listeners stop",
   ]
   assert talker._log_queue is None


def test_prettytuner_cleans_up_when_process_start_fails(monkeypatch, tmp_path):
   calls = []

   class LocalTalker:

      def __init__(self):
         self._log_queue = None

      def terminate(self):
         calls.append("talker terminate")

   class FakeRemote:

      def __init__(self, local, queue):
         del local, queue
         self._log_queue = None

      def log_prepare(self):
         calls.append("log prepare")
         self._log_queue = "log queue"

      def listening_start(self):
         calls.append("listeners start")

      def listening_stop(self):
         calls.append("listeners stop")

   class TuneProcess:
      pid = None

      def start(self):
         calls.append("process start")
         raise RuntimeError("start failed")

   class FakeContext:

      def Process(self, **kwargs):
         del kwargs
         return TuneProcess()

   monkeypatch.setattr(autotune, "RemoteTalker", FakeRemote)
   monkeypatch.setattr(autotune.multiprocessing, "Queue", lambda: object())
   monkeypatch.setattr(
      autotune.multiprocessing,
      "get_context",
      lambda method: FakeContext(),
   )
   talker = LocalTalker()

   with pytest.raises(RuntimeError, match="start failed"):
      autotune.prettytuner(talker=talker, d_tmp=str(tmp_path))

   assert calls == [
      "log prepare",
      "process start",
      "talker terminate",
      "listeners stop",
   ]
   assert talker._log_queue is None
