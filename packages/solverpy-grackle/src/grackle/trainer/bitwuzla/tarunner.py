from grackle.runner.bitwuzla import BitwuzlaRunner

class TARunner:

   def __init__(self, config):
      self.runner = BitwuzlaRunner(config)

   def run(self, config, seed, instance):
      result = self.runner.run(config, instance)
      return (result[0], result[1:]) if result else None

