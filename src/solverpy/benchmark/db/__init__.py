from .db import DB
from .providers.jsons import Jsons, JsonsStore
from .providers.solved import Solved
from .providers.status import Status
from .providers.loader import Loader, SlashLoader

def default():
   return DB([Jsons, Solved, Status])

__all__ = [DB, Jsons, JsonsStore, Solved, Status, Loader, 
           SlashLoader, default]

