from .db.bid import Bid
from .db.sid import Sid
from .db.outputs import Outputs
from .db.errors import Errors

def dbfiles():
   return [
      Bid(),
      Sid(),
   ]

def dbdebug():
   return [
      Bid(),
      Sid(),
      Outputs(),
      Errors(),
   ]

__all__ = [dbfiles, dbdebug]

