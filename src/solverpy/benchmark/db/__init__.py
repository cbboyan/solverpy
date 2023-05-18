from .db import DB
from .jsons import Jsons
from .solved import Solved
from .status import Status

def default():
   return DB([Jsons, Solved, Status])

__all__ = [DB, Jsons, default]

