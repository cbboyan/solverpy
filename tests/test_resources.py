from solverpy.tools import resources


def test_usage_reports_memory_and_cpu(monkeypatch):
   class Usage:
      ru_maxrss = 2048
      ru_utime = 1.25
      ru_stime = 0.75

   monkeypatch.setattr(resources, "_memory", lambda: (1024, 4096))
   monkeypatch.setattr(resources.resource, "getrusage", lambda kind: Usage())
   monkeypatch.setattr(resources.sys, "platform", "linux")

   message = resources.usage("checkpoint")

   assert message == (
      "resources [checkpoint] rss=1.0KiB peak_rss=2.0MiB "
      "vms=4.0KiB cpu=2.00s child_cpu=2.00s"
   )
