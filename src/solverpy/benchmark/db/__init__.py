from .db import DB
from .jsons import Jsons

def default():
   return DB([Jsons])

__all__ = [DB, Jsons, default]

