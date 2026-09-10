import logging

from solverpy.report.talker.logtalker import LogTalker


class FakeLimits:

   def __init__(self, timeout):
      self.timeout = timeout


class FakeSolver:

   def __init__(self, timeout):
      self.limits = FakeLimits(timeout)


BASE = 1000.0  # nonzero start: eval_status treats a falsy _last_time as unset


def make_talker(monkeypatch, cutoff):
   """A LogTalker wired for a single (solver, bid, sid) job under a fake clock."""
   clock = {"t": BASE}
   monkeypatch.setattr(
      "solverpy.report.talker.logtalker.time.perf_counter",
      lambda: clock["t"],
   )
   talker = LogTalker(headless=True)
   talker._total_nicks = {("bid", "sid"): "nick"}
   talker._nick_dw = 1
   talker._total_jobs = 1
   talker._job_index = 0
   job = (FakeSolver(cutoff), "bid", "sid")
   talker.eval_next(job)
   talker.eval_launch([])
   return talker, clock


def checkpoint_lines(caplog):
   return [r.message for r in caplog.records if "checkpoint @" in r.message]


def test_checkpoint_cutoff_set_from_job_limits(monkeypatch):
   talker, _ = make_talker(monkeypatch, cutoff=5)
   assert talker._checkpoint_cutoff == 5
   assert talker._checkpoint_next == 5


def test_reports_at_first_multiple_excluding_own_contribution(
      monkeypatch, caplog):
   caplog.set_level(logging.INFO, logger="solverpy.report.talker.logtalker")
   talker, clock = make_talker(monkeypatch, cutoff=5)

   clock["t"] = BASE + 0.05
   talker.eval_status(True)  # solved=1
   clock["t"] = BASE + 4.99
   talker.eval_status(True)  # solved=2, before the 5s checkpoint
   clock["t"] = BASE + 5.01
   talker.eval_status(False)  # crosses 5s; solved count as of just before it

   lines = checkpoint_lines(caplog)
   assert len(lines) == 1
   assert "5.0s" in lines[0]
   assert "solved=2" in lines[0]
   assert talker._checkpoint_next == 10


def test_solved_event_crossing_checkpoint_is_excluded(monkeypatch, caplog):
   caplog.set_level(logging.INFO, logger="solverpy.report.talker.logtalker")
   talker, clock = make_talker(monkeypatch, cutoff=5)

   clock["t"] = BASE + 0.05
   talker.eval_status(True)  # solved=1
   clock["t"] = BASE + 4.99
   talker.eval_status(True)  # solved=2
   clock["t"] = BASE + 5.01
   talker.eval_status(False)  # checkpoint @5s -> solved=2, advance to 10
   clock["t"] = BASE + 5.02
   talker.eval_status(True)  # solved=3, before the 10s checkpoint
   clock["t"] = BASE + 10.5
   talker.eval_status(True)  # crosses 10s; this solve itself is excluded

   lines = checkpoint_lines(caplog)
   assert len(lines) == 2
   assert "10.0s" in lines[1]
   assert "solved=3" in lines[1]
   assert talker._checkpoint_next == 15


def test_reset_on_next_job(monkeypatch):
   talker, clock = make_talker(monkeypatch, cutoff=5)
   clock["t"] = BASE + 5.01
   talker.eval_status(True)

   clock["t"] = BASE + 100.0
   job = (FakeSolver(2), "bid", "sid")
   talker.eval_next(job)
   talker.eval_launch([])

   assert talker._checkpoint_cutoff == 2
   assert talker._checkpoint_next == 2
   assert talker._solved == 0


def test_no_checkpoint_reports_without_cutoff(monkeypatch, caplog):
   caplog.set_level(logging.INFO, logger="solverpy.report.talker.logtalker")
   talker, clock = make_talker(monkeypatch, cutoff=0)

   clock["t"] = BASE + 50.0
   talker.eval_status(True)

   assert checkpoint_lines(caplog) == []
