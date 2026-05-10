import multiprocessing
from functools import wraps
from typing import Callable

def external(func: Callable) -> Callable:
   """
   Decorator that runs a function in a separate process to free memory on return.
   Uses fork explicitly so the inner closure does not need to be picklable
   (Python 3.14 changed the default start method on Linux to forkserver).
   """

   @wraps(func)
   def wrapper(*args, **kwargs):
      ctx = multiprocessing.get_context("fork")
      queue = ctx.Queue()

      def target():
         try:
            result = func(*args, **kwargs)
            queue.put((True, result))
         except Exception as e:
            queue.put((False, e))

      process = ctx.Process(target=target)
      process.start()
      process.join()

      if process.exitcode != 0:
         raise RuntimeError(
            f"Process failed with exit code {process.exitcode}")

      (success, data) = queue.get()
      if success:
         return data
      else:
         raise data

   return wrapper


def catching(func: Callable) -> Callable:
   """
   Decorator that catches exceptions and returns them as strings
   in the case an exception is raised.
   """

   @wraps(func)
   def wrapper(*args, **kwargs):
      try:
         return func(*args, **kwargs)
      except Exception as e:
         return str(e)

   return wrapper
