import logging

from ...builder.cvc5tune import Cvc5Tune

logger = logging.getLogger(__name__)

def autotuner(trains, devels, tuneargs, mk_builder):
   if "refs" not in trains:
      ref = trains["ref"] 
      idx = ref if (type(ref) is int) else 0
      trains["refs"] = [ trains["sidlist"][idx] ]
   trains["builder"] = mk_builder(trains, devels, tuneargs)
   return trains

def cvc5tune(trains, devels=None, tuneargs=None):
   return autotuner(trains, devels, tuneargs, Cvc5Tune)

