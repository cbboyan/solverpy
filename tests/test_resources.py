import io

from solverpy.tools import resources


def test_usage_reports_memory_and_cpu(monkeypatch):
   class Usage:
      ru_maxrss = 2048
      ru_utime = 1.25
      ru_stime = 0.75

   monkeypatch.setattr(resources, "_memory", lambda: (1024, None, 4096))
   monkeypatch.setattr(resources.resource, "getrusage", lambda kind: Usage())
   monkeypatch.setattr(resources.sys, "platform", "linux")

   message = resources.usage("checkpoint")

   assert message == (
      "resources [checkpoint] rss=1.0KiB peak_rss=2.0MiB "
      "vms=4.0KiB cpu=2.00s child_cpu=2.00s"
   )


def test_summary_reports_resources(monkeypatch):
   monkeypatch.setattr(
      resources,
      "_memory",
      lambda: (2 * 1024**3, 3 * 1024**3, 0),
   )
   usage = type("Usage", (), {"ru_maxrss": 4 * 1024**2})()
   monkeypatch.setattr(resources.resource, "getrusage", lambda kind: usage)
   monkeypatch.setattr(resources.sys, "platform", "linux")
   monkeypatch.setattr(resources.time, "monotonic", lambda: 751)

   assert resources.summary("main", 0) == (
      "Resources[main]: memory=2.0GiB peak=3.0GiB elapsed=12m31s"
   )


def test_summary_falls_back_to_peak_rss(monkeypatch):
   usage = type("Usage", (), {"ru_maxrss": 2048})()
   monkeypatch.setattr(resources, "_memory", lambda: (None, None, None))
   monkeypatch.setattr(resources.resource, "getrusage", lambda kind: usage)
   monkeypatch.setattr(resources.sys, "platform", "linux")
   monkeypatch.setattr(resources.time, "monotonic", lambda: 2)

   assert resources.summary("tuner", 0) == (
      "Resources[tuner]: memory=2.0MiB peak=2.0MiB elapsed=2s"
   )


def test_proc_memory_reads_consistent_linux_values(monkeypatch):
   status = [
      "Name:\tpython\n",
      "VmSize:\t4096 kB\n",
      "VmHWM:\t3072 kB\n",
      "VmRSS:\t2048 kB\n",
   ]
   monkeypatch.setattr(
      "builtins.open",
      lambda *args, **kwargs: io.StringIO("".join(status)),
   )

   assert resources._proc_memory() == (
      2 * 1024**2,
      3 * 1024**2,
      4 * 1024**2,
   )
