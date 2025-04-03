#!/usr/bin/env python
   
import logging

from ...tools import human
from ...task.bar import BuilderBar
from ...benchmark.reports import markdown

logger = logging.getLogger(__name__)

class Listener:

   def listen(self, message):
      logger.debug(f"listening: {message}")
      try:
         (key, content) = message
      except (TypeError, ValueError):
         logger.exception(f"Incorect message: '{message}'")
         return None
      if not (isinstance(content, tuple) or isinstance(content, list)):
         content = (content,)
      try:
         handler = getattr(self, key)
      except AttributeError:
         logger.warning(f"Unknown listener message: {key} (content: {content})")
         return None
      return handler(*content)

class AutotuneListener(Listener):

   def __init__(self):
      self.bar = None
      self.desc = "trial"
      self.iters = ""
      self.t_start = 0
      self.t_end = 0
      self.f_mod = None
      self.nick = None
      self.it = None
      self.values = None
      self.table = None
      self.header = None

   def result(self, val):
      return val
      
   def building(self, f_mod, total):
      logger.debug(f"building model: {f_mod}")
      self.bar = BuilderBar(total, self.desc)
   
   def built(self, score):
      self.bar.close()
      logger.debug(f"model {self.f_mod} built: score={score:.4f}")

   def iteration(self, n, total, loss):
      self.bar.done(loss)

   def trials(self, nick, iters, timeout):
      logger.info(f"Running tuning phase: {nick}\n> \n> ### Tuning `{nick}` ###\n> ")
      self.iters = f"/{iters}" if iters else ""
      self.header = ["it", nick, "score", "test.acc", "train.acc", "time"]
      self.table = []
   
   def trying(self, nick, it, values):
      self.it = it + 1
      self.desc = f"{nick}[{it+1}{self.iters}]"
      self.values = ", ".join("%.4f"%v if type(v) is float else str(v) for v in values)
      self.desc = f"[{it+1}{self.iters}] {self.values:8s}"

   #def tried(self, score, acc, trainacc, duration):
   def tried(self, stats):
      self.table.append((
         self.it, 
         self.values, 
         f"{stats['score']:.4f}", 
         human.humanacc(stats["valid_acc"]), 
         human.humanacc(stats["train_acc"]),
         human.humantime(stats["duration"]),
      ))
   
   def trialed(self, nick):
      lines = []
      lines.append("")
      lines.extend(markdown.table(self.header, self.table, key=lambda x: float(x[2])))
      lines.append("")
      logger.info("\n"+markdown.dump(lines, prefix="> "))

   def tuning(self, t_start):
      self.t_start = t_start

   def tuned(self, t_end):
      self.t_end = t_end

   def info(self, msg):
      logger.info(msg)

   def debug(self, msg):
      logger.debug(msg)

