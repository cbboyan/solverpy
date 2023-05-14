
class Solver:
   
   def __init__(self, name=None):
      self._name = name if name else type(self).__name__

   def __str__(self):
      return self.name
   
   @property
   def name(self):
      return self._name

   def solve(self, instance, strategy):
      output = self.run(instance, strategy)
      result = self.process(output)
      return (output, result)
   
   def valid(self, result):
      return ("status" in result) and ("runtime" in result)
   
   def solved(self, result):
      "Is the result a success?"
      return ("status" in result) and (result["status"] in self.success)

   def run(self, instance, strategy):
      "Run the solver with the strategy on the instatance."
      raise NotImlementedError()

   def process(self, output):
      "Process the solver output and create the result."
      raise NotImlementedError()
  
   @property
   def success(self):
      "The set of successful statuses."
      raise NotImlementedError()
  
   @property
   def timeout(self):
      "The set of timeout statuses."
      raise NotImlementedError()

