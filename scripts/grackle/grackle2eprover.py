#!/usr/bin/env python3

import sys
from grackle.runner.eprover import EproverRunner

if len(sys.argv) != 2:
   sys.stderr.write("usage %s: conf-file\n" % sys.argv[0])
   sys.exit(-1)

runner = EproverRunner()
params = open(sys.argv[1]).read().strip().split()
params = runner.parse(params)

print(runner.args(params))

