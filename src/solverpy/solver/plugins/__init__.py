from .db.bid import Bid
from .db.sid import Sid
from .db.outputs import Outputs
from .db.errors import Errors

def db():
   return [
      Bid(),
      Sid(),
   ]

def outputs(flatten=True, compress=True):
   return [
      Bid(),
      Sid(),
      Outputs(flatten, compress),
      Errors(flatten, compress),
   ]

__all__ = ["db", "outputs"]

