import os
from os import path

def parse(outdir, numRun, getparams=True):
   last = None
   params = None
   try:
      fs = [f for f in os.listdir(outdir) if "traj_%d"%numRun in f and f.endswith(".txt")]                             
      f0 = fs[0]
                                                                                                                       
      last = open(path.join(outdir,f0)).read().strip().split("\n")[-1]                                                 
      last = last.strip().split(",")                                                                                   
 
      params = None
      if getparams:
         params = [p.split("=") for p in last[5:]]
         params = {p[0].strip():p[1].strip("' ") for p in params}                                                         
      return (int(last[2]), float(last[1]), params)                                                                    
   except Exception as e:                                                                                              
      raise Exception(f"Error parsing paramils output (outdir='{outdir}' numRun='{numRun}' last='{last}' params='{params}' e='{e}'")

