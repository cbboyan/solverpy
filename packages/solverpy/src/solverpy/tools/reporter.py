from typing import TYPE_CHECKING
import os
import logging

if TYPE_CHECKING:
   from ..tools.typing import Report

logger = logging.getLogger(__name__)

# super-fence registry: language -> callable(content, options) -> str
# registered handlers are called during write to transform fenced blocks
_fences: dict = {}
_file = None


def fence(lang: str):
   """Register a super-fence handler for the given language."""
   def decorator(fn):
      _fences[lang] = fn
      return fn
   return decorator


def init(logpath: str) -> None:
   global _file
   mdpath = os.path.splitext(logpath)[0] + ".md"
   _file = open(mdpath, "w")
   logger.debug(f"Reporter writing to {mdpath}")


def write(content: str) -> None:
   if _file is None:
      return
   _file.write(content)
   if not content.endswith("\n"):
      _file.write("\n")
   _file.flush()


def add(report: "Report") -> None:
   from ..benchmark.reports.markdown import dump
   write(dump(report))


def close() -> None:
   global _file
   if _file:
      _file.flush()
      _file.close()
      _file = None
