from typing import TYPE_CHECKING

from .decorator import Decorator

if TYPE_CHECKING:
   from multiprocessing.managers import SyncManager


class Managed(Decorator):
   """Decorator that holds process-shared state connected via a Manager."""

   def connect(self, manager: "SyncManager") -> None:
      """Create process-shared state from the session-owned Manager."""

   def disconnect(self) -> None:
      """Discard process-shared proxies before their Manager is shut down."""
