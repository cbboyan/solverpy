import os

DEFAULT_NAME = "strats"
DEFAULT_DIR = os.getenv("PYSOLVE_STRATS", DEFAULT_NAME)

def path(sid):
   return os.path.join(DEFAULT_DIR, sid)

def load(sid):
   return open(path(sid)).read().strip()

def save(sid, strategy):
   f_sid = path(sid)
   os.makedirs(os.path.dirname(f_sid), exist_ok=True)
   open(f_sid, "w").write(strategy.strip())

