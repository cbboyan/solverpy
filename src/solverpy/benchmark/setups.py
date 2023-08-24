from .db import default
from . import launcher

def single(solver, 
           cores=4,
           sidlist=None, 
           sidfile="sids", 
           bidlist=None, 
           bidfile="bids",
           ref=True,
           flatten=True, 
           dataname="data/model",
           trains=None,
           db=None,
           ):

   if sidlist is None:
      with open(sidfile) as f:
         sidlist = f.read().strip().split("\n")
   if bidlist is None:
      with open(bidfile) as f:
         bidlist = f.read().strip().split("\n")
   if db is None:
      db = default()

   setup = {
      "solver": solver,
      "bidlist": bidlist,
      "sidlist": sidlist,
      "dataname": dataname,
      "ref": ref,
      "cores": cores,
      "db": db,
      "flatten": flatten,
      "sidnames": len(bidlist) == 1,
   }
   if trains:
      setup["trains"] = trains

   return setup

def launch(setup):
   launcher.init(setup)
   launcher.launch(**setup)

