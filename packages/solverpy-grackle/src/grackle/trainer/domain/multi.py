from .custom import CustomDomain
from .grackle import GrackleDomain, Condition


class MultiDomain(CustomDomain):

   def __init__(self, domains: list[GrackleDomain]):
      CustomDomain.__init__(self)
      self._domains: list[GrackleDomain] = []
      for domain in domains:
         self.add_domain(domain)

   def __repr__(self) -> str:
      args = [repr(dom) for dom in self._domains]
      return f"{type(self).__name__}([{','.join(args)}])"

   def reset(self) -> None:
      super().reset()
      self._domains = []

   def add_domain(self, domain: GrackleDomain) -> None:
      self._params.update(domain.params)
      self._defaults.update(domain.defaults)
      self._conditions.extend(domain.conditions)
      self._forbiddens.extend(domain.forbiddens)
      self._domains.append(domain)

   @property
   def domains(self) -> list[GrackleDomain]:
      return self._domains

   def join(self, params: dict[str, str], fixed: dict[str, str]) -> dict[str, str]:
      return params | fixed

   def split(self, params: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
      fixed: dict[str, str] = {}
      for domain in self._domains:
         (params, fixed0) = domain.split(params)
         fixed.update(fixed0)
      return (params, fixed)
