
class Solver:
   
   def __str__(self):
      return self.name
   
   @property
   def name(self):
      return type(self).__name__
  
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
      "Run the solver with the strategy on the instatance. Return the output."
      raise NotImlementedError()

   def process(self, output):
      "Process the solver output and create the result."
      raise NotImlementedError()
   
   @property
   def success(self):
      "The set of successful statuses."
      raise NotImlementedError()
  
