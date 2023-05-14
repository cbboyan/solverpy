import os, sys
import atexit, traceback
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DEFAULT_NAME = "solverpy_logs"
DEFAULT_DIR = os.getenv("SOLVERPY_LOGDIR", DEFAULT_NAME)

def filename():
   os.makedirs(DEFAULT_DIR, exist_ok=True)
   script = sys.argv[0]
   script = script.lstrip("./").replace("/","+")
   now = datetime.now()
   now = now.strftime("%y-%m-%d__%H:%M:%S")
   f_log = f"{script}__{now}.log"
   return os.path.join(DEFAULT_DIR, f_log)

def init():
   # set up logging to file
   logging.basicConfig(
      level=logging.DEBUG,
      format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
      filename=filename(),
      filemode="w")
   # define a Handler which writes INFO messages or higher to the sys.stderr
   console = logging.StreamHandler()
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

