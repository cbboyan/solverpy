import os
import logging

from ..benchmark.path import bids

NAME = "models"

logger = logging.getLogger(__name__)

class Builder:
   """Build the model from the training samples."""
    
   def __init__(self, dataname):
      """Construct the builder and store the dataname."""
      self._strats = []
      self._dataname = dataname

   def __repr__(self):
      return f"{type(self).__name__}({self._dataname})"

   def path(self):
      """Return the model filename."""
      return os.path.join(bids.dbpath(NAME), self._dataname)

   def reset(self, dataname):
      """Reset the dataname, for example, when a new loop is initiated."""
      self._dataname = dataname

   def build(self):
      """Build the model(s). Save the list of new strategies `self._strats`."""
      raise NotImlementedError()
   
   def apply(self, sid, model):
      """Combine the `model` with strategy `sid`."""
      raise NotImlementedError()
 
   @property
   def strategies(self):
      """Return all created strategies."""
      return self._strats
   
   def applies(self, sidlist, model):
      """Combine the `model` with several strategies `sidlist`."""
      new = []
      for ref in sidlist:
         new.extend(self.apply(ref, model))
      return new

