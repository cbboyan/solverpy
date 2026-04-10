from ..domain.multi import MultiDomain
from .default import DefaultDomain
from .actions import ActionsDomain
from .given import GivenDomain
from .keepdelete import KeepDeleteDomain

class FullDomain(MultiDomain):

   def __init__(self, flags=1, vals=3, low=2, high=2, keep=2, delete=2, conds=2, **kwargs):
      MultiDomain.__init__(self, domains=[
         DefaultDomain(),
         ActionsDomain(flags=flags, vals=vals),
         GivenDomain(low=low, high=high, conds=conds),
         KeepDeleteDomain(keep=keep, delete=delete, conds=conds),
      ])

