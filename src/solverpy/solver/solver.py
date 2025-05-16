
class Instance:
   pass

class Strategy:
   pass

class Solver:
   
   def __str__(self) -> str:
      return self.name

   def __repr__(self) -> str:
      return f"{type(self).__name__}()"
   
   @property
   def name(self) -> str:
      return type(self).__name__
  
   def solve(self, instance : Instance, strategy : Strategy) -> tuple[str, dict]:
      output = self.run(instance, strategy)
      result = self.process(output)
      return (output, result)
   
   def valid(self, result : dict) -> bool:
      """Is the result valid?"""
      return bool(result) and ("status" in result) and ("runtime" in result)
   
   def solved(self, result : dict) -> bool:
      """Is the result solved?"""
      return bool(result) and ("status" in result) and (result["status"] in self.success)

   def run(self, instance : Instance, strategy : Strategy) -> tuple[str, dict]:
      "Run the solver with the strategy on the instatance. Return the output."
      raise NotImlementedError()

   def process(self, output : str) -> dict:
      "Process the solver output and create the result."
      raise NotImlementedError()
   
   @property
   def success(self) -> set[str]:
      "The set of successful statuses."
      raise NotImlementedError()
  
