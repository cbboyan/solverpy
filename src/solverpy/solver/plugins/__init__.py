from .db.bid import Bid
from .db.errors import Errors
from .db.jsons import Jsons
from .db.outputs import Outputs
from .db.sid import Sid
from .db.solved import Solved
from .db.status import Status
from .db.yamls import Yamls

def dbfiles():
   return [
      Bid(),
      Sid(),
      Jsons(),
      Solved(),
      Errors(),
      Status(),
   ]

def dbdebug():
   return [
      Bid(),
      Sid(),
      Jsons(),
      #Yamls(),
      Solved(),
      Outputs(),
      Errors(),
      Status(),
   ]

__all__ = [dbfiles, dbdebug]

