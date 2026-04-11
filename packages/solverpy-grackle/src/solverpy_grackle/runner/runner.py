import os
import re
import sys
import hashlib
import subprocess
import multiprocessing
from typing import Any, TYPE_CHECKING

from .. import log
from ..tools import load_class
from ..trainer.domain.multi import MultiDomain
from .config import Params, RunnerConfig

if TYPE_CHECKING:
   from ..trainer.domain.grackle import GrackleDomain

def wrapper(args):
   (runner, (entity, inst)) = args
   return runner.run(entity, inst)

class Runner(object):
   config: RunnerConfig

   def __init__(self, config: RunnerConfig = RunnerConfig()):
      self.config = RunnerConfig(config)  # type: ignore[misc]
      self.default("direct", True)
      self.default("cores", 1)

   def default(self, key: str, val: Any) -> None:
      "Set a default value to the configuration."
      if key not in self.config:
         self.config[key] = val  # type: ignore[literal-required]

   def cmd(self, params: Params, inst: str) -> str:
      raise NotImplementedError("Abstract method `Runner.cmd` not implemented.")

   def process(self, out: bytes, inst: str) -> list[Any] | None:
      raise NotImplementedError("Abstract method `Runner.process` not implemented.")

   def success(self, result: str) -> bool:
      raise NotImplementedError("Abstract method `Runner.success` not implemented.")

   @property
   def domain(self):
      raise NotImplementedError("Abstract method `Runner.domain` not implemented.")
   
   def run(self, entity: Params, inst: str) -> list[Any] | None:
      cmd = self.cmd(entity, inst)
      try:
         out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as err:
         out = err.output
      except BaseException as err:
         log.fatal("ERROR(Grackle): Runner failed: %s" % (str(err) or err.__class__.__name__))
         sys.exit(-1)
      res = self.process(out, inst)
      if not res:
         msg = "\nERROR(Grackle): Error while evaluating on instance %s!\ncommand: %s\nparams: %s\noutput: \n%s\n" % (inst, cmd, entity, out.decode())
         log.fatal(msg)
         return None
      return res

   def runs(self, cis: list[tuple[Any, str]]) -> Any:
      assert "cores" in self.config
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
   def __init__(self, config: RunnerConfig = RunnerConfig()):
      Runner.__init__(self, config)
      self.default("dir", "confs")
      self.default("prefix", "conf-")
      assert "direct" in self.config
      assert "dir" in self.config
      if not self.config["direct"]:
         os.system("mkdir -p %s" % self.config["dir"])
      domcfg = {x: str(y) for (x,y) in config.items() if x.startswith("domain")}
      self.load_domain(domcfg)

   def name(self, params: Params, save: bool = True) -> str:
      assert "prefix" in self.config
      assert "dir" in self.config
      args = self.repr(params).replace("="," ")
      conf = "%s%s" % (self.config["prefix"], hashlib.sha224(args.encode()).hexdigest())
      if save:
         open(os.path.join(self.config["dir"],conf),"w").write(args)
      return conf

   def recall(self, conf: str) -> Params:
      assert "dir" in self.config
      args = open(os.path.join(self.config["dir"],conf)).read().strip()
      return self.parse(args.split())

   def parse(self, lst: list[str]) -> Params:
      ps: Params = {}
      while lst:
         key = lst.pop(0).lstrip("-").strip()
         val = lst.pop(0).strip()
         ps[key] = val
      return ps

   def cmd(self, params: Params, inst: str = "") -> str:
      args = " ".join(["-%s %s"%(p,params[p]) for p in sorted(params)])
      return "%%s %s" % args

   def repr(self, params: Params) -> str:
      return " ".join(["%s=%s"%(p,params[p]) for p in sorted(params)])
  
   def clean(self, params: Params) -> Params | None:
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
   
   def run(self, entity: str | Params, inst: str) -> list[Any] | None:
      params = entity if self.config["direct"] else self.recall(entity)  # type: ignore[arg-type]
      return Runner.run(self, params, inst)  # type: ignore[arg-type]

   def default_domain(self, maker: Any, **kwargs: Any) -> None:
      if not self._domain:
         self._domain = maker(**kwargs)

   def load_domain(self, cfg: dict[str, str]) -> None:
      self._domain: "GrackleDomain | None" = None
      self._conds: dict[str, dict[str, list[str]]] = {}
      names = [x for x in cfg if "." not in x]
      domains: list["GrackleDomain"] = []
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
      for (slave, master, values) in self._domain.conditions:
         if slave not in self._conds:
            self._conds[slave] = {}
         self._conds[slave][master] = values

   def conditions(self, s_conds: str) -> dict[str, dict[str, frozenset[str]]]:
      conds: dict[str, dict[str, frozenset[str]]] = {}
      for line in s_conds.strip().split("\n"):
         if "|" not in line:
            continue
         (name, cond) = line.strip().split("|")
         name = name.strip()
         (cname, vals) = cond.split(" in ")
         cname = cname.strip()
         vals_set = frozenset([x.strip() for x in vals.strip().strip("{}").split(",")])
         if name not in conds:
            conds[name] = {}
         conds[name][cname] = vals_set
      return conds

   @property
   def domain(self) -> "GrackleDomain | None":
      return self._domain

   @domain.setter
   def domain(self, value: "GrackleDomain") -> None:
      self._domain = value

