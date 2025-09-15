"""
This module defines the database for benchmarking. 
"""

from .db import DB
from .providers.jsons import Jsons, JsonsStore
from .providers.solved import Solved
from .providers.status import Status
from .providers.loader import Loader, SlashLoader


def default(delfix: (int | str | None) = None) -> DB:
   """
   Create a database with default providers:
   [`Jsons`][solverpy.benchmark.db.providers.jsons],
   [`Solved`][solverpy.benchmark.db.providers.solved], and
   [`Status`][solverpy.benchmark.db.providers.status].

   Args:
      delfix (): 
         Prefix to remove from problem names for
         [`Solved`][solverpy.benchmark.db.providers.solved] and
         [`Status`][solverpy.benchmark.db.providers.status]. 
         See the `delfix` in [`Setup`][solverpy.setups.setup.Setup]
         for the value format.

   Returns: 
      The database.
   """
   return DB([
      Jsons.Maker(),
      Solved.Maker(delfix=delfix),
      Status.Maker(delfix=delfix)
   ])


__all__ = [
   "DB", "Jsons", "JsonsStore", "Solved", "Status", "Loader", "SlashLoader",
   "default"
]
