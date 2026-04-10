#!/usr/bin/env python3

if __name__ == '__main__':
   import sys
   import json
   from grackle.tools import load_class
   
   RESULT="\nResult for ParamILS: %s, %s, %s, 1000000, %s"
   
   def run():
      conf = json.loads(sys.argv[1])
      runner = load_class(conf["cls"])(config=conf)
      runner.config["cutoff"] = int(float(sys.argv[4]))
      inst = sys.argv[2]
      seed = sys.argv[6]
      #(quality,clock) = runner.run(params, inst)[:2]

      params = runner.parse(sys.argv[7:])
      fixed = conf["fixed"] if "fixed" in conf else {}
      params = runner.clean(params)
      params.update(fixed)
      res = runner.run(params, inst)
      if not res: res = [9999999999, 9999999999] # use conf["penalty.error"]
      (quality, clock) = res[:2]
   
      print(RESULT % ("OK", clock, quality, seed))
   
   if len(sys.argv) < 2:
      print("usage: %s runner_config instance spec time cutoff seed arg1 val1 ..." % sys.argv[0])
   else:
      run()

