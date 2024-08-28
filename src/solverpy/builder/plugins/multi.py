import logging

from .trains import Trains

logger = logging.getLogger(__name__)

class MultiTrains(Trains):

   def __init__(self, dataname):
      self._trains = []
      self._dataname = dataname

   def dispatch(self, t):
      self._trains.append(t)

   def apply(self, function):
      for t in self._trains:
         function(t)
   
   def register(self, solver):
      super().register(solver)
      self._solver = solver
      for t in self._trains:
         t._solver = solver

   def reset(self, dataname=None, filename="train.in"):
      if dataname:
         self._dataname = dataname
      self.apply(lambda x: x.reset(dataname=dataname, filename=filename))

   def finished(self, *args, **kwargs):
      self.apply(lambda x: x.finished(*args, **kwargs))

   def extract(self, *args, **kwargs):
      self.apply(lambda x: x.extract(*args, **kwargs))
   
   def save(self, *args, **kwargs):
      self.apply(lambda x: x.save(*args, **kwargs))
    
   def stats(self, *args, **kwargs):
      self.apply(lambda x: x.stats(*args, **kwargs))

   def compress(self, *args, **kwargs):
      self.apply(lambda x: x.compress(*args, **kwargs))

