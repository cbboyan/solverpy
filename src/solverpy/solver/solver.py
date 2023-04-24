


class Solver:
   
   def __init__(self):
      pass

   def solve(self, instance, strategy):
      output = self.run(instance, strategy)
      result = self.process(output)
      return (output, result)
   
   def valid(self, result):
      return ("status" in result) and ("runtime" in result)

   def run(self, instance, strategy):
      "Run the solver with the strategy on the instatance."
      raise NotImlementedError()

   def process(self, output):
      "Process the solver output and create the result."
      raise NotImlementedError()

   def solved(self, result):
      "Is the result a success?"
      raise NotImlementedError()

