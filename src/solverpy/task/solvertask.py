#!/usr/bin/env python3

import subprocess
from .task import Task

class SolverTask(Task):

   def __init__(self, solver, bid, sid, problem):
      self.solver = solver
      self.bid = bid
      self.sid = sid
      self.problem = problem

   def __str__(self):
      return f"{self.solver}:{self.sid} @ {self.bid} / {self.problem}"

   def run(self):
      return self.solver.solve(self.instance, self.strategy)

   def status(self, result):
      if not self.solver.valid(result):
         return None
      return self.solver.solved(result)

   @property
   def instance(self):
      return (self.bid, self.problem)

   @property
   def strategy(self):
      return self.sid

