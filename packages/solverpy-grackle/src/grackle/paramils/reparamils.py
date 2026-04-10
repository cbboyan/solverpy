import sys
import os
from os import path, system
import subprocess
import time

import grackle.paramils.results

def reparamils(scenariofile, outdir, cwd, binary="param_ils_2_3_run.rb", count=1, N=10, validN="800", init="1", out=None, time_limit=None, restarts=False):
   def run(numRun, currentInit):
      arg = [binary, "-numRun", str(numRun), "-scenariofile", scenariofile, "-N", str(N), "-validN", validN, "-output_level", "0", "-userunlog", "0"] 
      if open(os.path.join(cwd,currentInit)).read().strip():
         arg.extend(["-init", currentInit])
      outlog = open((out % numRun) if out else os.devnull, "w")
      outlog.write(f"# CMD: {' '.join(arg)}\n")
      return subprocess.Popen(arg,stdout=outlog,close_fds=True,cwd=cwd)

   #if not out:
   #   out = open(os.devnull, 'w')
     
   running = {numRun:run(numRun,init) for numRun in range(count)}
   fresh = count
   elder = (None,None,None)
   it = 1
   log = ""
   print(">> --- TRAIN ITER %d ---" % it)
   start = time.time()
   if time_limit:
      end = time.time() + time_limit
   else:
      end = float("inf")
   iter_start = time.time()
   adult = False
   while running:
      time.sleep(2)
      sys.stdout.flush()

      log0 = log
      log = ""
      for numRun in running:
         (n,q,_) = grackle.paramils.results.parse(outdir, numRun, getparams=False)
         log += "%2s:%3s (%8.1f)\t" % (numRun,n,q) 
         #print(numRun, n, q)
         if restarts and not adult and numRun is not elder[0] and n == N:
            adult = True
            stable_len = max(20, time.time() - iter_start)
            stable_time = time.time() + stable_len
            print("%6s> %s" % (int(time.time()-start),log))
            print(">> first young (%d) reached N (=%d); entering stabilization phase (%s seconds)" % (numRun, N, stable_len))
            sys.stdout.flush()
      if log != log0:
         print("%6s> %s" % (int(time.time()-start),log))
         sys.stdout.flush()
     
      if not adult or time.time() < stable_time:
         if time.time() < end:
            continue
         else:
            print(">> time limit reached. terminating.")
            sys.stdout.flush()

      winner = None
      bestq = None
      for numRun in running:
         (n,q,params) = grackle.paramils.results.parse(outdir, numRun)
         if n == N:
            if (not winner) or q < winner[1]:
               winner = (numRun,q,params)
         if (not bestq) or q < bestq[1]:
               bestq = (numRun,q,params)
      if not winner: # when timeout-ing
         if elder[0] is not None: 
            winner = elder
         else:
            winner = bestq

      print(">> winner: %s with Q = %s" % (winner[0],  winner[1]))
      sys.stdout.flush()

      if time.time() > end:
         elder = winner
         break

      if elder[0] is not None and int(1000*winner[1]) >= int(1000*elder[1]):
         print(">> no improvement. terminating.")
         sys.stdout.flush()
         elder = winner
         break

      kills = set(running.keys())
      kills.remove(winner[0])
      #print("> terminating: ", kills)
      for kill in kills:
         running[kill].terminate()

      time.sleep(1)
      for kill in kills:
         if not running[kill].poll():
            print(">> killing: ", kill)
            try:
               running[kill].kill()
            except:
               pass
      
      keep = running[winner[0]]
      params = winner[2]
      init0 = " ".join(["%s %s"%(x,params[x]) for x in sorted(params)])
      f_init = "init_%02d"%it
      open(path.join(cwd,f_init),"w").write(init0)
      running = {numRun:run(numRun,f_init) for numRun in range(fresh,fresh+count-1)}
      running[winner[0]] = keep

      fresh += (count-1)
      elder = winner
      it += 1
      print(">> --- TRAIN ITER %d ---" % it)
      sys.stdout.flush()
      iter_start = time.time()
      adult = False

   #print("> terminating: ", running.keys())
   for kill in running:
      running[kill].terminate()
   time.sleep(1)
   for kill in running:
      if not running[kill].poll():
         print(">> killing: ", kill)
         try:
            running[kill].kill()
         except:
            pass

   #print("RES: ", elder[2])
   return elder[2]

def launch(scenario, domains, init, insts, cwd, timeout, cores, restarts, logs):
   system("rm -fr %s" % cwd)
   system("mkdir -p %s" % cwd)

   f_scenario = path.join(cwd, "scenario.txt")
   f_params = path.join(cwd, "params.txt")
   f_instances = path.join(cwd, "instances.txt")
   f_empty = path.join(cwd, "empty.tst")
   f_init = path.join(cwd, "init_00")
   
   open(f_scenario,"w").write(scenario)
   open(f_params,"w").write(domains)
   open(f_instances,"w").write("\n".join(insts))
   open(f_empty,"w").write("")
   open(f_init,"w").write(" ".join(["%s %s"%(x,init[x]) for x in sorted(init)]))

   params = reparamils(
      "scenario.txt",
      path.join(cwd,"paramils-out"),
      cwd,
      count=cores,
      N=len(insts),
      validN=str(len(insts)),
      init="init_00",
      #out=open(path.join(cwd,"paramils.out"),"w") if logs else None,
      out=path.join(cwd,"run_%02d.log") if logs else None,
      restarts=restarts,
      time_limit=timeout)

   return params

