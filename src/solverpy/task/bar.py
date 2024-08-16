import datetime
from tqdm import tqdm

RED = '\033[91m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
END = '\033[0m'

#BAR_DEFAULT = "{desc}: {percentage:6.2f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]{postfix}"
#BAR_RUNNING = "{desc}: {percentage:6.2f}%|{bar}| {n_fmt}/{total_fmt} {errors} [{elapsed}<{remaining}]{postfix}"
#BAR_SOLVING = "{desc}: {percentage:6.2f}%|{bar}| {n_fmt}/{total_fmt} {solved}/{unsolved}/{errors}/{solved_eta} [{elapsed}<{remaining}]{postfix}"
BAR_DEFAULT = "{desc}: {percentage:6.2f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{speta}]{postfix}"
BAR_BUILDER = "{desc}: {percentage:6.2f}%|{bar}| {n_fmt}/{total_fmt} {loss} [{elapsed}<{remaining}]{postfix}"
BAR_RUNNING = "{desc}: {percentage:6.2f}%|{bar}| {n_fmt}/{total_fmt} {errors} [{elapsed}<{speta}]{postfix}"
BAR_SOLVING = "{desc}: {percentage:6.2f}%|{bar}| {n_fmt}/{total_fmt} {solved}/{unsolved}/{errors}/{solved_eta} [{elapsed}<{speta}]{postfix}"

class DefaultBar(tqdm):
   
   def __init__(self, total, desc, ascii="┈─═━", colour="green", bar_format=BAR_DEFAULT, *args, **kwargs):
      tqdm.__init__(self, total=total, desc=desc, bar_format=bar_format, ascii=ascii, colour=colour, *args, **kwargs)
   
   @property
   def format_dict(self):
      d = super().format_dict
      speta = d["elapsed"] * (d["total"] or 0) / max(d["n"], 1)
      speta -= d["elapsed"]
      speta = str(datetime.timedelta(seconds=int(speta)))
      if speta.startswith("0:"):
         speta = speta[2:]
      d.update(speta=speta)
      return d

   def status(self, status, n=1):
      self.update(n)

class BuilderBar(tqdm):
   
   def __init__(self, total, desc, ascii="┈─═━", colour="green", bar_format=BAR_BUILDER, *args, **kwargs):
      self._loss = []
      tqdm.__init__(self, total=total, desc=desc, bar_format=bar_format, ascii=ascii, colour=colour, *args, **kwargs)
   
   @property
   def format_dict(self):
      d = super().format_dict
      d.update(loss=self._loss)
      return d

   def done(self, loss, n=1):
      self._loss = "/".join(f"{x:.4f}" for x in loss)
      self.update(n)

class RunningBar(DefaultBar):

   def __init__(self, total, desc, bar_format=BAR_RUNNING, *args, **kwargs):
      self._errors = 0
      DefaultBar.__init__(self, total, desc, bar_format=bar_format, *args, **kwargs)
   
   @property
   def format_dict(self):
      d = super().format_dict
      asc = f"!{self._errors}"
      if self._errors:
         asc = f"{RED}{asc}{END}"
      d.update(errors=asc)
      return d

   def status(self, status, n=1):
      if status is None:
         self._errors += n
      self.update(n)

class SolvingBar(RunningBar):

   def __init__(self, total, desc, bar_format=BAR_SOLVING, ascii="┈─═━", colour="blue", *args, **kwargs):
      self._solved = 0
      self._unsolved = 0
      RunningBar.__init__(self, total, desc, bar_format=bar_format, ascii=ascii, colour=colour, *args, **kwargs)

   @property
   def format_dict(self):
      d = super().format_dict
      #total_time = d["elapsed"] * (d["total"] or 0) / max(d["n"], 1)
      solved_eta = int(self._solved * (d["total"] / max(d["n"],1)))
      d.update(
        solved=f"{PURPLE}+{self._solved}{END}", 
        unsolved=f"{BLUE}{self._unsolved}{END}", 
        solved_eta=f"{PURPLE}?{solved_eta}{END}",
      )
      return d

   def status(self, status, n=1):
      if status is True:
         self._solved += n
      elif status is False:
         self._unsolved += n
      else: # status is None:
         self._errors += n
      self.update(n)
     
