from .db import DB
from .providers.jsons import Jsons, JsonsStore
from .providers.solved import Solved
from .providers.status import Status
from .providers.loader import Loader, SlashLoader

def default(delfix=None):
   return DB([Jsons.Maker(), Solved.Maker(delfix=delfix), Status.Maker(delfix=delfix)])

__all__ = ["DB", "Jsons", "JsonsStore", "Solved", "Status", "Loader", 
           "SlashLoader", "default"]

