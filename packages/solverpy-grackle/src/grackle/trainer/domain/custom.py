from typing import Any
from collections.abc import Mapping

from .grackle import GrackleDomain, Condition


class CustomDomain(GrackleDomain):

   def __init__(self, **kwargs: Any):
      GrackleDomain.__init__(self, **kwargs)
      self.reset()

   def reset(self) -> None:
      self._params: dict[str, list[Any] | str] = {}
      self._defaults: dict[str, str] = {}
      self._conditions: list[Condition] = []
      self._forbiddens: list[str] = []

   def add_param(self, name: str, domain: list[Any] | str, default: str | None = None) -> None:
      assert(default or not isinstance(domain, str))
      self._params[name] = domain
      self._defaults[name] = str(default or (domain if isinstance(domain, str) else domain[0]))

   def add_dep(self, slave: str, master: str, values: list[Any]) -> None:
      self._conditions.append((slave, master, values))

   @property
   def params(self) -> dict[str, list[Any] | str]:
      return self._params

   @property
   def defaults(self) -> dict[str, str]:
      return self._defaults

   @property
   def conditions(self) -> list[Condition]:
      return self._conditions

   @property
   def forbiddens(self) -> list[str]:
      return self._forbiddens
