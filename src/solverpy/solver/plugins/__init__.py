from .db.bid import Bid
from .db.sid import Sid
from .db.outputs import Outputs
from .db.errors import Errors

def db():
   return [
      Bid(),
      Sid(),
   ]

def outputs():
   return [
      Bid(),
      Sid(),
      Outputs(),
      Errors(),
   ]

__all__ = [db, outputs]

