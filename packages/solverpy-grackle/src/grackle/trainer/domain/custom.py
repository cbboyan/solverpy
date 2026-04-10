from .grackle import GrackleDomain

class CustomDomain(GrackleDomain):
   
   def __init__(self, **kwargs):
      GrackleDomain.__init__(self, **kwargs)
      self.reset()
   
   def reset(self):
      self._params = {}
      self._defaults = {}
      self._conditions = []
      self._forbiddens = []
   
   def add_param(self, name, domain, default=None):
      assert(default or not isinstance(domain,str))
      self._params[name] = domain
      self._defaults[name] = str(default or domain[0])

   def add_dep(self, slave, master, values):
      self._conditions.append((slave, master, values))

   @property
   def params(self):
      return self._params

   @property
   def defaults(self):
      return self._defaults

   @property 
   def conditions(self):
      return self._conditions

   @property
   def forbiddens(self):
      return self._forbiddens

