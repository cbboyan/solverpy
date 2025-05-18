#!/usr/bin/env python3

import subprocess
from .task import Task

class ShellTask(Task):

   def __init__(self, cmd):
      self.cmd = cmd

   def run(self) -> bytes:
      try:
         output = subprocess.check_output(self.cmd, shell=True,
            stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as e:
         output = e.output
      except Exception as e:
         print("ERROR: Shell task failed: %s" % self.cmd)
         raise e
      return output

