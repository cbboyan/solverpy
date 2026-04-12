#!/bin/bash

grackle-ramparils '{"direct": true, "cores": 1, "cls": "solverpy_grackle.runner.eprover.EproverRunner", "prefix": "eprover-", "penalty": 10000000, "domain1": "solverpy_grackle.trainer.eprover.default.DefaultDomain", "timeout": 1, "penalty.error": 10000000000}' tptp/test/isa/mesh/prob_00015_000413__42351008_1.p 1 -slots 0
#grackle-ramparils '{"direct": true, "cores": 1, "cls": "solverpy_grackle.runner.eprover.EproverRunner", "prefix": "eprover-", "penalty": 10000000, "domain1": "solverpy_grackle.trainer.eprover.default.DefaultDomain", "timeout": 1, "penalty.error": 10000000000}' tptp/agatha.p 1 -slots 0
