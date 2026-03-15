from typing import TYPE_CHECKING
import os, sys, io
import atexit, traceback
from datetime import datetime
import requests
import socket
import logging
import yaml

from ..benchmark.path import bids
from ..solver.object import SolverPyObj

if TYPE_CHECKING:
   from ..setups.setup import Setup

logger = logging.getLogger(__name__)

NAME = "logs"


def ntfy(setup: "Setup", msg: str) -> None:
   if (not setup) or ("ntfy" not in setup):
      return
   channel = setup["ntfy"]
   try:
      hostname = socket.gethostname()
      requests.post(f"https://ntfy.sh/{channel}", data=f"{hostname}: {msg}")
   except IOError as e:
      logger.warning(f"> Warning: ntfy I/O error ({e})")


def filename() -> str:
   d_logs = bids.dbpath(NAME)
   os.makedirs(d_logs, exist_ok=True)
   script = sys.argv[0]
   script = script.lstrip("./").replace("/", "--")
   now = datetime.now()
   now = now.strftime("%y-%m-%d__%H:%M:%S")
   f_log = f"{now}__{script}.log"
   return os.path.join(d_logs, f_log)


def init_yaml() -> None:

   def representer(dumper, obj: SolverPyObj):
      r = obj.represent()
      if type(r) is str:
         return dumper.represent_str(r)
      elif type(r) is list:
         return dumper.represent_list(r)
      elif type(r) is dict:
         return dumper.represent_dict(r)
      else:
         return dumper.represent_str(str(r))

   yaml.add_multi_representer(SolverPyObj, representer)


def init() -> None:
   # set up logging to file
   logging.basicConfig(
      level=logging.DEBUG,
      format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
      filename=filename(),
      filemode="w")
   # define a Handler which writes INFO messages or higher to the sys.stderr
   #console = logging.StreamHandler()
   console = logging.StreamHandler(
      io.TextIOWrapper(os.fdopen(sys.stderr.fileno(), "wb")))

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
   init_yaml()


def terminating() -> None:
   logger.info("Logger terminated.")
   if "last_traceback" in dir(sys):
      msg = traceback.format_exception(sys.last_type, sys.last_value,
                                       sys.last_traceback)
      msg = "".join(msg)
      logger.error(f"Last exception:\n{msg}")
