import os
import logging

from ..provider import Provider
#from ...path import bids, sids
from ....solver.plugins.db.outputs import Outputs

logger = logging.getLogger(__name__)

class Loader(Provider):
      
   def __init__(self, bid, sid, limit=None, flatten=False):
      Provider.__init__(self, bid, sid, limit, False)
      self.outputs = Outputs(flatten=flatten) 

   def query(self, task):
      self.outputs.solver = task.solver 
      f = self.outputs.path(task.instance, task.strategy)
      if not os.path.isfile(f):
         return None
      #logger.debug(f"loading output for task {task} from {f}")
      with open(f) as fr:
         output = fr.read()
      result = task.solver.process(output)
      task.solver.update(task.instance, task.strategy, output, result)
      #logger.debug(f"result = {result}")
      return result

class FlattenLoader(Loader):

   def __init__(self, bid, sid, limit=None):
      Loader.__init__(self, bid, sid, limit, flatten=True)


