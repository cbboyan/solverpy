from .. import log

class StageRunner(Runner):

   def split(self, params):
      raise NotImplementedError("Abstract method not implemented.")

   def join(self, main, extra):
      raise NotImplementedError("Abstract method not implemented.")

   def domains(self, config, init=None):
      raise NotImplementedError("Abstract method not implemented.")

   def run(self, params, inst):
      joint = self.join(params, self.config["extra"]) if "extra" in self.config else params
      res = self.runner.run(self, joint, inst)
      if not res:
         msg = "ERROR(Grackle): Original params were: %s\n" % params)
         log.fatal(msg)
      return res

   # the below just translate to the base runner calls

   def cmd(self, params, inst):
      return self.runner.cmd(self, params, inst)

   def default(self, key, val):
      return self.runner.default(self, key, val)

   def process(self, out, inst):
      return self.runner.process(self, out, inst)

   def success(self, result):
      return self.runner.success(self, result)

   def runs(self, cis):
      return self.runner.runs(self, cis)

   def name(self, params, save=True):
      return self.runner.name(self, params, save)

   def recall(self, conf):
      return self.runner.recall(self, conf)

   def parse(self, lst):
      return self.runner.parse(self, lst)

   def cmd(self, params):
      return self.runner.cmd(self, params)

   def repr(self, params):
      return self.runner.repr(self, params)

   def clean(self, params):
      return self.runner.clean(self, params)

         

