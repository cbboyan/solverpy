import signal
from types import SimpleNamespace

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
