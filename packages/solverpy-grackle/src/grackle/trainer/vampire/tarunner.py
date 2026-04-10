from grackle.runner.vampire import VampireRunner

class TARunner:

   def __init__(self, config):
      self.runner = VampireRunner(config)

   def run(self, config, seed, instance):
      result = self.runner.run(config, instance)
      #print("VAMPIRE", instance, result)
      return (result[0], result[1:]) if result else None

