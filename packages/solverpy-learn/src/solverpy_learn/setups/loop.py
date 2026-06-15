import sys
import logging
import gc
import time

from solverpy.benchmark import evaluation as evaluator
from solverpy.report import log
from solverpy.tools import reporter
from solverpy.benchmark.reports import markdown
from solverpy.setups.common import default
from solverpy.setups.setup import Setup
from solverpy.setups.evalset import Evalset
from solverpy.setups.runtime import Runtime, initialize
from solverpy.report.talker.evaltalker import EvalTalker
from solverpy.report.talker.talker import Talker
from solverpy.setups import experiment
from solverpy.tools.resources import summary as resource_summary, usage
from solverpy_learn.report.talker.looptalker import LoopTalker

logger = logging.getLogger(__name__)


def loopinit(setup: Setup, evalset: Evalset) -> Evalset:
   assert "basedataname" in evalset
   assert "plugin" in evalset
   assert "it" in setup
   base = evalset["basedataname"]
   it = setup["it"]
   if it == 0:
      filename = "train.in"
   else:
      evalset["previous_trains"] = evalset["plugin"].path()
      filename = "addon.in"
   evalset["dataname"] = f"{base}/loop{it:02d}"
   evalset["plugin"].reset(evalset["dataname"], filename)
   return evalset


def looping(setup: Setup, evalset: Evalset) -> Evalset:
   assert "dataname" in evalset
   evalset["basedataname"] = evalset["dataname"]
   assert "max_proofs" in setup
   if setup["max_proofs"] > 0:
      evalset["proofs"] = {}
   return evalset


def boot(setup: Setup) -> Runtime:
   assert "options" in setup
   headless = "headless" in setup["options"]
   MakeTalker = LoopTalker if "loops" in setup else EvalTalker
   talker = MakeTalker(headless=headless)
   runtime = initialize(setup)
   talker._log_queue = runtime.log_queue
   talker.log_start()
   setup["talker"] = talker
   return runtime


def oneloop(
   setup: Setup,
   evalset: Evalset,
) -> Evalset:
   started_at = time.monotonic()

   assert "options" in setup
   options = setup["options"]

   def is_last() -> bool:
      return ("loops" in setup) and (setup.get("it") == setup["loops"])

   def trains_compress() -> None:
      if "plugin" not in evalset:
         return
      evalset["plugin"].train_data_snapshot()
      if ("compress" in options) and ("no-compress-trains" not in options):
         assert "chunk_size" in setup
         evalset["plugin"].compress(
            chunk_size=setup["chunk_size"],
            cores=setup.get("cores"),
         )

   def trains_merge() -> None:
      assert "plugin" in evalset
      plugin = evalset["plugin"]
      if ("previous_trains" not in evalset) or is_last():
         return
      previous = evalset["previous_trains"]
      if not plugin.exists():
         logger.warning(f"No trains found: {plugin.path()}.")
         logger.warning(f"Reusing previous trains: {previous}.")
         plugin.link(previous)
         if "max_proofs" in setup and setup["max_proofs"] > 0:
            setup["max_proofs"] += 1
            logger.info(f"Increasing max_proofs to: {setup['max_proofs']}")
      plugin.merge(evalset["previous_trains"], "train.in")
      plugin.reset(filename="train.in")

   def model_build() -> None:
      if "builder" not in setup:
         return
      builder = setup["builder"]
      if builder and not is_last():
         builder.build(setup["talker"])
         setup["news"] = builder.strategies
         logger.info("New ML strategies:\n" + "\n".join(setup["news"]))

   def train_data_stats(paths=None) -> list[dict]:
      assert "plugin" in evalset
      stats = evalset["plugin"].train_data_stats(evalset["label"], paths)
      return [stats] if isinstance(stats, dict) else stats

   assert "dataname" in evalset
   assert "label" in evalset
   it = setup['it'] if 'it' in setup else 0
   dataname = evalset['dataname']
   report = markdown.newline() + markdown.heading(
      f"Evaluation `{dataname}`", level=2)
   reporter.add(report)
   logger.info(f"Running evaluation loop {it} on data {dataname}.")
   logger.info(resource_summary("main", started_at))
   logger.debug(usage(f"loop {it} start: {dataname}"))
   try:
      if (it > 0) or ("start_dataname" not in evalset):
         evaluator.launch(evalset, **setup)
         if "plugin" not in evalset:
            return evalset
         generated_paths = evalset["plugin"].path()
         trains_compress()
         trains_merge()
         generated = train_data_stats(generated_paths)
         current = train_data_stats()
         seen = {stat["path"] for stat in generated}
         setup["talker"].train_data(
            generated + [stat for stat in current if stat["path"] not in seen])
      elif "plugin" in evalset:
         logger.info(
            f"Evaluation skipped.  Starting with data {evalset['start_dataname']}"
         )
         evalset["plugin"].reset(evalset["start_dataname"])
         setup["talker"].train_data(train_data_stats())
      model_build()
      return evalset
   finally:
      logger.info(resource_summary("main", started_at))
      logger.debug(usage(f"loop {it} end: {dataname}"))


def launch(setup: Setup) -> Setup | None:
   experiment(setup)

   runtime = None
   started_at = time.monotonic()
   dataname = "unknown"
   if "trains" in setup and "dataname" in setup["trains"]:
      dataname = setup["trains"]["dataname"]
   logger.info(resource_summary("main", started_at))
   logger.debug(usage(f"run start: {dataname}"))

   try:
      runtime = boot(setup)

      def do_loop(evalset: Evalset | None) -> None:
         if evalset is None: return
         oneloop(setup, evalset)

      def do_iter(evalset: Evalset | None) -> None:
         if evalset is None: return
         evalset["strategies"].extend(setup["news"] if "news" in setup else [])
         oneloop(setup, evalset)

      trains = setup["trains"] if "trains" in setup else None
      devels = setup["devels"] if "devels" in setup else None
      default(trains, "label", "training") if trains else None
      default(devels, "label", "development") if devels else None

      log.ntfy(setup, "solverpy: init")
      evaluator.init(setup)
      if "loops" in setup:
         default(setup, "max_proofs", 0)
         default(setup, "chunk_size", 1_000_000)
         setup["it"] = 0
         if trains:
            looping(setup, trains)
            loopinit(setup, trains)
         if devels:
            looping(setup, devels)
            loopinit(setup, devels)
      do_loop(devels)
      do_loop(trains)
      if "loops" in setup:
         while setup["it"] < setup["loops"]:
            gc.collect()
            log.ntfy(setup, f"solverpy: iter #{setup['it']}")
            setup["it"] += 1
            if devels:
               loopinit(setup, devels)
            if trains:
               loopinit(setup, trains)
               if "builder" in setup:
                  setup["builder"].reset(trains["dataname"])
            do_iter(devels)
            if devels and (setup['it'] == setup["loops"]):
               break
            do_iter(trains)
      log.ntfy(setup, "solverpy: done")
      return setup
   except KeyboardInterrupt:
      logger.warning("Terminated (keyboard interrupt)")
      print("Terminated (keyboard interrupt)")
      sys.exit(0)
   finally:
      try:
         if runtime:
            setup["talker"].log_stop()
            runtime.shutdown()
      finally:
         logger.info(resource_summary("main", started_at))
         logger.debug(usage(f"run end: {dataname}"))
