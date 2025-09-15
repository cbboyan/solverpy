"""
The plugins module.
"""

from .db.bid import Bid
from .db.sid import Sid
from .db.outputs import Outputs
from .db.errors import Errors

def db():
   """Solver plugins for DB connection."""
   return [
      Bid(),
      Sid(),
   ]

def outputs(flatten=True, compress=True):
   """Debugging plugins."""
   return [
      Bid(),
      Sid(),
      Outputs(flatten, compress),
      Errors(flatten, compress),
   ]

__all__ = ["db", "outputs"]

