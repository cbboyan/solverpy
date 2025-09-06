import multiprocessing
from functools import wraps
from typing import Callable


def external(func: Callable) -> Callable:
   """
    Decorator that runs a function in a separate process.
    """

   @wraps(func)
   def wrapper(*args, **kwargs):
      queue = multiprocessing.Queue()

      def target():
         try:
            result = func(*args, **kwargs)
            queue.put((True, result))
         except Exception as e:
            queue.put((False, e))

      process = multiprocessing.Process(target=target)
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
