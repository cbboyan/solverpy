from .solverpy import SolverPy
from .plugins.db.outputs import Outputs

class Reloader(SolverPy):

   def __init__(self, solver, plugins=[]):
      self.solver = solver
      SolverPy.__init__(
            self, solver.limits.timeout, solver.limits.limit, plugins)
      self.outputs = Outputs()
      self.outputs.register(self.solver)

   def run(self, instance, strategy):
      f = self.outputs.path(instance, strategy)
      with open(f) as fr:
         return fr.read()

   def process(self, output):
      return self.solver.process(output)

   def valid(self, result):
      return self.solver.valid(result)
   
   def decorate(self, cmd, instance, strategy):
      return self.solver.decorate(cmd, instance, strategy)
   
   def update(self, instance, strategy, output, result):
      return self.solver.update(instance, strategy, output, result)
   
   def translate(self, instance, strategy):
      return self.solver.translate(instance, strategy)

   @property
   def name(self):
      return f"{super().name}({self.solver.name})"

   @property
   def success(self):
      return self.solver.success

   @property
   def timeouts(self):
      return self.solver.timeouts



