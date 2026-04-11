#!/bin/bash

grackle-ramparils '{"direct": true, "cores": 16, "cls": "solverpy_grackle.runner.eprover.EproverRunner", "prefix": "eprover-", "penalty": 10000000, "domain1": "solverpy_grackle.trainer.eprover.default.DefaultDomain", "timeout": 1, "dir": "confs", "penalty.error": 10000000000}' tptp/agatha.p 1 -slots 0
