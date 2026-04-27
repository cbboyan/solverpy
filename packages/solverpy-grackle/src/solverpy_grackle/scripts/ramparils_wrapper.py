import sys
import json
from solverpy_grackle.tools import load_class

RESULT = "#%%# RamParIls #%%# %s, %s, %s"


def main():
   if len(sys.argv) < 4:
      print("usage: %s runner_config instance cutoff_time -param1 val1 ..." % sys.argv[0])
      return

   conf = json.loads(sys.argv[1])
   cutoff = int(float(sys.argv[3]))
   conf["timeout"] = cutoff
   runner = load_class(conf["cls"])(config=conf)
   inst = sys.argv[2]
   runner.config["cutoff"] = int(float(sys.argv[3]))

   params = runner.parse(sys.argv[4:])
   fixed = conf.get("fixed", {})
   params = runner.clean(params)
   params.update(fixed)
   res = runner.run(params, inst)
   if res:
      (quality, clock, status) = res[:3]
      print(RESULT % (status, clock, quality))

