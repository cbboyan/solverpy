"""Lightweight process resource snapshots for debug logging."""

import os
import resource
import sys
import time

from .human import humanbytes


def _proc_memory() -> tuple[int | None, int | None, int | None]:
   """Return RSS, peak RSS, and virtual memory from Linux procfs."""
   values = {}
   try:
      with open("/proc/self/status", encoding="ascii") as stream:
         for line in stream:
            key, _, value = line.partition(":")
            if key in ("VmRSS", "VmHWM", "VmSize"):
               values[key] = int(value.split()[0]) * 1024
   except (OSError, ValueError):
      pass
   return (
      values.get("VmRSS"),
      values.get("VmHWM"),
      values.get("VmSize"),
   )


def _memory() -> tuple[int | None, int | None, int | None]:
   """Return current RSS, peak RSS, and virtual memory when available."""
   current_rss, peak_rss, virtual = _proc_memory()
   if current_rss is not None:
      return current_rss, peak_rss, virtual
   try:
      with open("/proc/self/statm", encoding="ascii") as stream:
         total, resident = map(int, stream.readline().split()[:2])
      page_size = os.sysconf("SC_PAGE_SIZE")
      return resident * page_size, None, total * page_size
   except (OSError, ValueError):
      return None, None, None


def _duration(seconds: float) -> str:
   seconds = int(seconds)
   minutes, seconds = divmod(seconds, 60)
   hours, minutes = divmod(minutes, 60)
   days, hours = divmod(hours, 24)
   if days:
      return f"{days}d{hours}h{minutes}m{seconds}s"
   if hours:
      return f"{hours}h{minutes}m{seconds}s"
   if minutes:
      return f"{minutes}m{seconds}s"
   return f"{seconds}s"


def summary(label: str, started_at: float) -> str:
   """Format current/peak memory and elapsed time for concise info logging."""
   current_rss, peak_rss, _ = _memory()
   own = resource.getrusage(resource.RUSAGE_SELF)
   peak_scale = 1 if sys.platform == "darwin" else 1024
   if peak_rss is None:
      peak_rss = int(own.ru_maxrss * peak_scale)
   if current_rss is None:
      current_rss = peak_rss
   memory = humanbytes(
      current_rss, precision=1, separator="", binary_units=True)
   peak = humanbytes(
      peak_rss, precision=1, separator="", binary_units=True)
   elapsed = _duration(time.monotonic() - started_at)
   return (
      f"Resources[{label}]: memory={memory} peak={peak} elapsed={elapsed}"
   )


def usage(label: str) -> str:
   """Format current memory and cumulative CPU usage for debug logs."""
   current_rss, peak_rss, virtual = _memory()
   own = resource.getrusage(resource.RUSAGE_SELF)
   children = resource.getrusage(resource.RUSAGE_CHILDREN)
   peak_scale = 1 if sys.platform == "darwin" else 1024
   fields = [f"resources [{label}]"]
   if current_rss is not None:
      fields.append(
         "rss=" + humanbytes(
            current_rss,
            precision=1,
            separator="",
            binary_units=True,
         ))
   fields.append(
      "peak_rss=" + humanbytes(
         peak_rss if peak_rss is not None else int(own.ru_maxrss * peak_scale),
         precision=1,
         separator="",
         binary_units=True,
      ))
   if virtual is not None:
      fields.append(
         "vms=" + humanbytes(
            virtual,
            precision=1,
            separator="",
            binary_units=True,
         ))
   fields.extend([
      f"cpu={own.ru_utime + own.ru_stime:.2f}s",
      f"child_cpu={children.ru_utime + children.ru_stime:.2f}s",
   ])
   return " ".join(fields)
