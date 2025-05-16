import os
import gzip
import logging

from ..provider import Provider
#from ...path import bids, sids
from ....solver.plugins.db.outputs import Outputs

logger = logging.getLogger(__name__)

class Loader(Provider):
      
   def __init__(self, bid, sid, limit=None, flatten=True):
      Provider.__init__(self, bid, sid, limit, False)
      self.outputs = Outputs(flatten=flatten) 

   def query(self, task):
      self.outputs.solver = task.solver 
      f = self.outputs.path(task.instance, task.strategy)
      #logger.debug(f"loading output for task {task} from {f}")
      if os.path.isfile(f+".gz"):
         fr = gzip.open(f+".gz","rb")
      elif os.path.isfile(f):
         fr = open(f,"rb")
      else:
         return None
      output = fr.read().decode()
      fr.close()
      result = task.solver.process(output)
      task.solver.update(task.instance, task.strategy, output, result)
      #logger.debug(f"result = {result}")
      return result

class SlashLoader(Loader):

   def __init__(self, bid, sid, limit=None):
      Loader.__init__(self, bid, sid, limit, flatten=False)


