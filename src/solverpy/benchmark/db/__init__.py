from .db import DB
from .providers.jsons import Jsons
from .providers.solved import Solved
from .providers.status import Status

def default():
   return DB([Jsons, Solved, Status])

__all__ = [DB, Jsons, default]

