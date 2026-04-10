
class Trainer:
   
   def __init__(self, runner, config={}):
      self.runner = runner
      self.config = dict(config)
      self.default("instance_budget", None)
      self.default("log", False)

   def improve(self, state, conf, insts):
      pass
   
   def default(self, key, val):
      "Set a default value to the configuration."
      if key not in self.config:
         self.config[key] = val

   def trainlimit(self, n_inst):
      if self.config["instance_budget"]:
         timeout = n_inst * self.config["instance_budget"]
         timeout = min(self.config["timeout"], timeout)
      else:
         timeout = self.config["timeout"]
      return timeout

