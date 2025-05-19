from typing import Any
from .object import SolverPyObj

class Solver(SolverPyObj):
   
   def __str__(self) -> str:
      return self.name

   @property
   def name(self) -> str:
      return self.__class__.__name__
  
   def solve(self, instance : Any, strategy : Any) -> Any:
      output = self.run(instance, strategy)
      result = self.process(output)
      return (output, result)
   
   def valid(self, result : dict) -> bool:
      """Is the result valid?"""
      return bool(result) and ("status" in result) and ("runtime" in result)
   
   def solved(self, result : dict) -> bool:
      """Is the result solved?"""
      return bool(result) and ("status" in result) and (result["status"] in self.success)

   def run(self, instance : Any, strategy : Any) -> str:
      "Run the solver with the strategy on the instatance. Return the output."
      del instance, strategy
      raise NotImplementedError()

   def process(self, output : str) -> dict:
      "Process the solver output and create the result."
      del output
      raise NotImplementedError()
   
   @property
   def success(self) -> set[str]:
      "The set of successful statuses."
      raise NotImplementedError()
  
