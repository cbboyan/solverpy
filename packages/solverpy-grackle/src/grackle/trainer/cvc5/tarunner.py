from grackle.runner.cvc5 import Cvc5Runner

class TARunner:

   def __init__(self, config):
      self.runner = Cvc5Runner(config)

   def run(self, config, seed, instance):
      result = self.runner.run(config, instance)
      #print("CVC5", instance, result)
      return (result[0], result[1:]) 

