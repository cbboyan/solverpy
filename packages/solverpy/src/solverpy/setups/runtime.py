import multiprocessing
from typing import Iterable

from ..solver.plugins.managed import Managed
from .setup import Setup


class Runtime:
   """Process resources owned by one complete learning-loop session."""

   def __init__(self, plugins: Iterable[Managed]) -> None:
      unique = {id(p): p for p in plugins}
      self._plugins = list(unique.values())
      self._manager = multiprocessing.get_context("forkserver").Manager()
      try:
         self.log_queue = self._manager.Queue()
         for p in self._plugins:
            p.connect(self._manager)
      except BaseException:
         self.shutdown()
         raise

   def shutdown(self) -> None:
      """Disconnect proxies and stop the shared Manager process."""
      if self._manager is None:
         return
      try:
         for p in self._plugins:
            p.disconnect()
      finally:
         self._manager.shutdown()
         self._manager = None


def initialize(setup: Setup) -> Runtime:
   """Initialize Managed plugins from setup["plugins"] with a shared Manager."""
   plugins = [p for p in setup.get("plugins", []) if isinstance(p, Managed)]
   return Runtime(plugins)
