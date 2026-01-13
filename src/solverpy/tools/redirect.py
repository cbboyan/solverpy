from typing import Any, TextIO, BinaryIO, Callable, TypeVar
import sys
import os
import ctypes
from sys import platform

libc = ctypes.CDLL(None)

if platform == "linux" or platform == "linux2":
   c_stdout = ctypes.c_void_p.in_dll(libc, 'stdout')
   c_stderr = ctypes.c_void_p.in_dll(libc, 'stderr')
elif platform == "darwin":
   c_stdout = ctypes.c_void_p.in_dll(libc, '__stdoutp')
   c_stderr = ctypes.c_void_p.in_dll(libc, '__stderrp')
elif platform == "win32":
   c_stdout = ctypes.c_void_p.in_dll(libc, 'stdout')
   c_stderr = ctypes.c_void_p.in_dll(libc, 'stderr')


class Redirector(object):

   def __init__(self, f_log: str) -> None:
      self._f_log = f_log

   def __enter__(self) -> "Redirector":
      self._redir = start(self._f_log)
      return self

   def __exit__(self, *args: Any) -> bool:
      del args
      finish(*self._redir)
      return False


def redirect(std: TextIO, fd: int) -> None:
   libc.fflush(c_stdout)
   libc.fflush(c_stderr)
   std_fd = std.fileno()  # note that std stays open
   os.dup2(fd, std_fd)


def start(f_log: str) -> tuple[BinaryIO, int, int]:
   s_log = open(f_log, mode="wb")
   dup_out = os.dup(sys.stdout.fileno())
   dup_err = os.dup(sys.stderr.fileno())
   redirect(sys.stdout, s_log.fileno())
   redirect(sys.stderr, s_log.fileno())
   return (s_log, dup_out, dup_err)


def finish(s_log: BinaryIO, dup_out: int, dup_err: int) -> None:
   redirect(sys.stdout, dup_out)
   redirect(sys.stderr, dup_err)
   os.close(dup_out)
   os.close(dup_err)
   s_log.close()


R = TypeVar("R")

def call(
   target: Callable[..., R],
   f_log: str,
   *args: Any,
   **kwargs: Any,
) -> R:
   try:
      with Redirector(f_log):
         return target(*args, **kwargs)
   #except (Exception, KeyboardInterrupt) as e:
   except Exception:
      raise   # propagate exception to the parent
   raise
