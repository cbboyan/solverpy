import os
import re
import sys
import hashlib
import subprocess
import multiprocessing

from .. import log
from ..tools import load_class
from ..trainer.domain.multi import MultiDomain

def wrapper(args):
   (runner, (entity, inst)) = args
   return runner.run(entity, inst)

class Runner(object):
   def __init__(self, config={}):
      self.config = dict(config)
      self.default("direct", True)
      self.default("cores", 1)

   def default(self, key, val):
      "Set a default value to the configuration."
      if key not in self.config:
         self.config[key] = val

   def cmd(self, params, inst):
      raise NotImplementedError("Abstract method `Runner.cmd` not implemented.")

   def process(self, out, inst):
      raise NotImplementedError("Abstract method `Runner.process` not implemented.")

   def success(self, result):
      raise NotImplementedError("Abstract method `Runner.success` not implemented.")

   @property
   def domain(self):
      raise NotImplementedError("Abstract method `Runner.domain` not implemented.")
   
   def run(self, params, inst):
      cmd = self.cmd(params, inst)
      try:
         out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
         #out = out.decode()
      except subprocess.CalledProcessError as err:
         out = err.output
      except BaseException as err:
         log.fatal("ERROR(Grackle): Runner failed: %s" % (err.message or err.__class__.__name__))
         sys.exit(-1)
      res = self.process(out, inst)
      if not res:
         msg = "\nERROR(Grackle): Error while evaluating on instance %s!\ncommand: %s\nparams: %s\noutput: \n%s\n"%(inst,cmd,self.repr(params),out.decode())
         log.fatal(msg)
         return None
      return res

   def runs(self, cis):
      pool = multiprocessing.Pool(self.config["cores"])
      try:
         results = pool.map_async(wrapper, zip([self]*len(cis),cis)).get(10000000)
      except BaseException as err:
         pool.terminate()
         log.fatal("ERROR(Grackle): Evaluation failed: %s" % (str(err) or err.__class__.__name__))
         raise err
         #sys.exit(-1)
      else:
         pool.close()
      if None in results:
         log.fatal("ERROR(Grackle): Evaluation failed, look around for more info.")
         #sys.exit(-1)
      return zip(cis, results)

class GrackleRunner(Runner):
   def __init__(self, config={}):
      Runner.__init__(self, config)
      self.default("dir", "confs")
      self.default("prefix", "conf-")
      if not self.config["direct"]:
         os.system("mkdir -p %s" % self.config["dir"])
      domcfg = {x:y for (x,y) in config.items() if x.startswith("domain")}
      self.load_domain(domcfg)

   def name(self, params, save=True):
      args = self.repr(params).replace("="," ")
      #conf = "%s%s" % (self.config["prefix"], sha.sha(args).hexdigest())
      conf = "%s%s" % (self.config["prefix"], hashlib.sha224(args.encode()).hexdigest())
      if save:
         open(os.path.join(self.config["dir"],conf),"w").write(args)
      return conf

   def recall(self, conf):
      args = open(os.path.join(self.config["dir"],conf)).read().strip()
      return self.parse(args.split())
   
   def parse(self, lst):
      ps = {}
      while lst:
         key = lst.pop(0).lstrip("-").strip()
         val = lst.pop(0).strip()
         ps[key] = val
      return ps
   
   def cmd(self, params): # ? need inst ?
      args = " ".join(["-%s %s"%(p,params[p]) for p in sorted(params)])
      return "%%s %s" % args

   def repr(self, params):
      return " ".join(["%s=%s"%(p,params[p]) for p in sorted(params)])
  
   def clean(self, params):
      assert self.domain
      # clean default values
      params = {x:params[x] for x in params if params[x] != self.domain.defaults[x]}
      # clean conditioned arguments
      delme = set()
      idle = False


      while not idle:
         idle = True
         for x in params:
            if x not in self._conds:
               continue
            for y in self._conds[x]:
               val = params[y] if y in params else self.domain.defaults[y]
               if val not in self._conds[x][y]:
                  delme.add(x)
                  break
         for x in delme:
            del params[x]
            idle = False
         delme.clear()
      return params
   
   def run(self, entity, inst):
      params = entity if self.config["direct"] else self.recall(entity)
      return Runner.run(self, params, inst)

   def default_domain(self, maker, **kwargs):
      if not self._domain:
         self._domain = maker(**kwargs)
  
   def load_domain(self, cfg):
      self._domain = None
      names = [x for x in cfg if "." not in x]
      domains = []
      for key in sorted(names):
         prf = f"{key}."
         args = {x[len(prf):]:y for (x,y) in cfg.items() if x.startswith(prf)}
         dom = load_class(cfg[key])(**args)
         domains.append(dom)
      if len(domains) == 1:
         self._domain = domains[0]
      elif len(domains) > 1:
         self._domain = MultiDomain(domains)
      assert self._domain
      self._conds = {}
      for (slave,master,domain) in self._domain.conditions:
         if slave not in self._conds:
            self._conds[slave] = {}
         self._conds[slave][master] = domain
         
   def conditions(self, s_conds):
      conds = {}
      for line in s_conds.strip().split("\n"):
         if "|" not in line:
            continue
         (name, cond) = line.strip().split("|")
         name = name.strip()
         (cname, vals) = cond.split(" in ")
         cname = cname.strip()
         vals = vals.strip().strip("{}").split(",")
         vals = frozenset([x.strip() for x in vals])
         if name not in conds:
            conds[name] = {}
         conds[name][cname] = vals
      return conds

   @property
   def domain(self):
      return self._domain

   @domain.setter
   def domain(self, value):
      self._domain = value

