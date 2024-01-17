import os, sys, io
import atexit, traceback
from datetime import datetime
import requests
import socket
import logging

from ..benchmark.path import bids

logger = logging.getLogger(__name__)

NAME = "logs"

def ntfy(setup, msg):
   if (not setup) or ("ntfy" not in setup):
      return
   channel = setup["ntfy"]
   try:
      hostname = socket.gethostname()
      requests.post(f"https://ntfy.sh/{channel}", data=f"{hostname}: {msg}")
   except IOError as e:
      logger.warining(f"> Warning: ntfy I/O error ({e})")

def filename():
   d_logs = bids.dbpath(NAME)
   os.makedirs(d_logs, exist_ok=True)
   script = sys.argv[0]
   script = script.lstrip("./").replace("/","-")
   now = datetime.now()
   now = now.strftime("%y-%m-%d__%H:%M:%S")
   f_log = f"{script}__{now}.log"
   return os.path.join(d_logs, f_log)

def init():
   # set up logging to file
   logging.basicConfig(
      level=logging.DEBUG,
      format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
      filename=filename(),
      filemode="w")
   # define a Handler which writes INFO messages or higher to the sys.stderr
   #console = logging.StreamHandler()
   console = logging.StreamHandler(io.TextIOWrapper(os.fdopen(sys.stderr.fileno(), "wb")))

   console.setLevel(logging.INFO)
   # set a format which is simpler for console use
   #formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
   formatter = logging.Formatter("%(asctime)-12s: %(levelname)-8s %(message)s")
   #formatter = logging.Formatter("%(asctime)-12s: %(message)s")
   # tell the handler to use this format
   console.setFormatter(formatter)
   # add the handler to the root logger
   logging.getLogger("").addHandler(console)
   logger.info("Logger running.")
   atexit.register(terminating)

def terminating():
   logger.info("Logger terminated.")
   if "last_traceback" in dir(sys):
      msg = traceback.format_exception(sys.last_type, sys.last_value, sys.last_traceback)
      msg = "".join(msg)
      logger.error(f"Last exception:\n{msg}")

