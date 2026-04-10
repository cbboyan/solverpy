import os
import time
import requests
import socket

FATAL_LOG = os.path.join(os.getenv("HOME"),"grackle-errors.log")

def ntfy(state, msg):
   if not state.ntfy:
      return
   try:
      hostname = socket.gethostname()
      requests.post(f"https://ntfy.sh/{state.ntfy}", data=f"{hostname}: {msg}")
   except IOError as e:
      print(f"> Warning: ntfy I/O error ({e})")

def active(state, mastered):
   print("> ACTIVE CONFIGURATIONS: %d" % len(state.active))
   for conf in sorted(state.active, key = lambda x: state.nicks[x]):
      info = "\n".join(["%s%s"%(inst,state.evals.results[conf][inst]) for inst in sorted(mastered[conf])])
      print("> %s: masters %d evals" % (state.nicks[conf], len(mastered[conf])))
      print(info)
   print(">")

def training(state, bpis):
   print("> TRAINING PERFORMANCE:")
   #(results, bests) = db_trains
   for c in sorted(bpis, key = lambda x: state.nicks[x]):
      info = "\n".join(["%s%s"%(i,state.trains.results[c][i]) for i in sorted(bpis[c])])
      print("> %s: masters %d trains" % (state.nicks[c], len(bpis[c])))
      print(info)
   print(">")

def improving(state, conf, insts):
   print("> Improving %s on %d trains." % (state.nicks[conf], len(insts)))

def iter(state):
   state.it += 1
   print(">")
   print("> === ITER %d ===" % state.it)
   print(">")
   ntfy(state, f"grackle runing iter #{state.it}")

def update(db, confs):
   print("> Evaluating %d configurations on %s." % (len(confs), db.name))

def status(state, db):
   runtime = (time.time() - state.start_time) / 60
   msg = "> STATUS @ %d (%s): %s, %.2f, %.2f (%.2f, %.4f)" % ((runtime,)+db.status())
   print(msg)
   ntfy(state, msg[2:].split(",")[0])

def candidates(state, candidates, avgs):
   print("TRAINING CANDIDATES:")
   for c in candidates:
      print("%s: %s" % (state.nicks[c], avgs[c]))
   print

def finished(state):
   print("> Nothing more to do. Terminating.")
   print(">")
   print("> FINAL CONFIGURATIONS: %d" % len(state.active))
   for conf in sorted(state.active, key = lambda x: state.nicks[x]):
      params = state.trains.runner.recall(conf)
      rep = state.trains.runner.repr(params)
      print("> %s: %s" % (state.nicks[conf], rep))
   ntfy(state, "grackle finished")

def timeout(state):
   print("> Timeout: Not enough time for training. Terminating after %s seconds." % (time.time() - state.start_time))
   ntfy(state, "grackle timed out")

def timestamp(t_start, msg, prog="GRACKLE"):
   t_elapsed = int(time.time() - t_start)
   t_hour = t_elapsed / 3600
   t_min = (t_elapsed % 3600) / 60
   t_sec = t_elapsed % 60
   print("> [%02d:%02d:%02d] %s: %s" % (t_hour, t_min, t_sec, prog, msg))

def improved(state, conf):
   print(conf)
   params = state.trains.runner.recall(conf)
   rep = state.trains.runner.repr(params)
   print("> INVENTED CONFIG: %s: %s" % (conf, rep))
   print(">")
   strat = state.trains.runner.args(params)
   strat = "\n".join(f"> {line}" for line in strat.split("\n"))
   print("> INVENTED STRATEGY: %s:\n%s" % (conf, strat))
   print(">")

def notnew(state, conf):
   print("> Invented config already known: %s" % state.nicks[conf] if conf in state.nicks else conf)
   print(">")

def nickname(conf, nick):
   print("> NICKNAME: %s = %s" % (nick, conf))

def init(state, f_init, conf):
   print("> Loaded initial config %s from %s" % (conf, f_init))

def inits(state):
   print(">")
   print("> INITIAL CONFIGURATIONS: %d" % len(state.alls))
   for conf in sorted(state.alls, key = lambda x: state.nicks[x]):
      params = state.trains.runner.recall(conf)
      rep = state.trains.runner.repr(params)
      print("> INIT CONFIG: %s: %s" % (state.nicks[conf], rep))

def scenario(state, ini, unused=None):
   show = lambda dic: "\n>   "+"\n>   ".join(["%s=%s"%(x,dic[x]) for x in sorted(dic)])
   print(">" )
   print("> === GRACKLE RUNNING ===")
   print(">")
   print("> Loaded parameters:")
   print("> cores = %s" % state.cores)
   print("> best = %s" % state.best)
   print("> tops = %s" % state.tops)
   print("> rank = %s" % state.rank)
   print("> timeout = %s" % state.timeout)
   print("> atavistic = %s" % state.atavistic)
   print("> selection = %s" % state.selection)
   print("> trains.data = %s" % ini["trains.data"])
   print("> trains.runner.config: %s" % show(state.trains.runner.config))
   uns = show(state.unsolved) if state.unsolved else "<not used>"
   print("> unsolved: %s" % uns)
   if "evals.data" in ini:
      print("> evals.data = %s" % ini["evals.data"])
      print("> evals.runner.config:  %s" % show(state.evals.runner.config))
   else:
      print("> evals = trains")
   print("> inits = %s" % ini["inits"])
   #print("> runner = %s" % ini["runner"])
   #print("> trainer = %s" % ini["trainer"])
   print("> trainer.config: %s" % show(state.trainer.config))
   print("> domain = %s" % repr(state.trainer.runner.domain))

   print(">")
   print("> Loaded %d evals" % len(state.evals.insts))
   print("> Loaded %d trains" % len(state.trains.insts))

   if unused:
      print(">")
      print("> Grackle Warning: Unrecognized parameters: %s" % sorted(unused))
      print(">")

def tuner(nick, i, n):
   print(">>")
   print(">> === TUNER[%d/%d]: %s ===" % (i,n,nick))

def msg(m):
   print(m)

def error(m):
   print(m)

def fatal(m):
   error(m)
   f = open(FATAL_LOG, "a")
   f.write(m)
   f.close()

def missing(insts):
   print("> Error: Missing features for the following training instances:")
   print("\n".join(sorted(insts)))

def kdtree(data):
   print("> Computing kd-tree for data matrix shape %s." % str(data.shape))

def kdnone():
   print("> Out of unsolved problems.")

def kdselect(state, conf, insts, selected, info):
   print("> The selected strategy %s masters %d instances." % (conf, len(insts)))
   print("> Selected %d similar unsolved problems:" % len(selected))
   for idx in selected:
      (n,rank) = info[idx]
      print("%s ~[%d]~ %s" % (state.kdindices[idx], rank, insts[n]))

