from tqdm import tqdm

BAR_DEFAULT = "{desc}: {percentage:6.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]{postfix}"

BAR_SOLVED = "{desc}: {percentage:6.3f}%|{bar}| {n_fmt}/{total_fmt} +{solved}/-{failed}/!{errors}/?{solved_eta:.0f} [{elapsed}<{remaining}]{postfix}"

class SolvedBar(tqdm):

   def __init__(self, *args, **kwargs):
      self._solved = 0
      self._failed = 0
      self._errors = 0
      tqdm.__init__(self, bar_format=BAR_SOLVED, *args, **kwargs)

   @property
   def format_dict(self):
      d = super(SolvedBar, self).format_dict
      #total_time = d["elapsed"] * (d["total"] or 0) / max(d["n"], 1)
      solved_eta = self._solved * (d["total"] / max(d["n"],1))
      d.update(
        solved=self._solved, 
        failed=self._failed, 
        errors=self._errors, 
        solved_eta=solved_eta,
      )
      return d

   def update_solved(self, n=1):
      self._solved += n

   def update_failed(self, n=1):
      self._failed += n

   def update_errors(self, n=1):
      self._errors += n

#

def default(total, desc, *args, **kwargs):
   return tqdm(total=total, desc=desc, bar_format=BAR_DEFAULT, ascii="┈─═━", colour="green", *args, **kwargs)

def solved(total, desc, *args, **kwargs):
   #return SolvedBar(total=total, desc=desc, ascii="░▒█")
   return SolvedBar(total=total, desc=desc, ascii="┈─═━", colour="blue", *args, **kwargs)
   #return SolvedBar(total=total, desc=desc, ascii="┈▏ ▎ ▍ ▌ ▋ ▊ ▉█", colour="blue")



