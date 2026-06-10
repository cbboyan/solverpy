"""Lightweight process resource snapshots for debug logging."""

import os
import resource
import sys

from .human import humanbytes


def _memory() -> tuple[int | None, int | None]:
   """Return current RSS and virtual memory in bytes when available."""
   try:
      with open("/proc/self/statm", encoding="ascii") as stream:
         total, resident = map(int, stream.readline().split()[:2])
      page_size = os.sysconf("SC_PAGE_SIZE")
      return resident * page_size, total * page_size
   except (OSError, ValueError):
      return None, None


def usage(label: str) -> str:
   """Format current memory and cumulative CPU usage for debug logs."""
   current_rss, virtual = _memory()
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
         int(own.ru_maxrss * peak_scale),
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
