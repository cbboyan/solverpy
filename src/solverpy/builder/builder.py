import os
import logging

from ..benchmark.path import bids

NAME = "models"

logger = logging.getLogger(__name__)

class Builder:
    
   def __init__(self, dataname):
      self._strats = []
      self._dataname = dataname

   def __repr__(self):
      return f"{type(self).__name__}({self._dataname})"

   def path(self):
      return os.path.join(bids.dbpath(NAME), self._dataname)

   def reset(self, dataname):
      self._dataname = dataname

   def build(self):
      "Build the model(s). Save the list of invented strategies `_strats`."
      raise NotImlementedError()
   
   def apply(self, sid, model):
      raise NotImlementedError()
 
   @property
   def strategies(self):
      "Return all created strategies."
      return self._strats
   
   def applies(self, sidlist, model):
      new = []
      for ref in sidlist:
         new.extend(self.apply(ref, model))
      return new

