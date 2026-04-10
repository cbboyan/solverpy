from unittest.mock import MagicMock


def mock_domain(self, cfg):
   self._domain = MagicMock()
   self._conds = {}


def z3_domain(self, cfg):
   from grackle.trainer.z3.options import OptionsDomain
   self._domain = OptionsDomain()
   self._conds = {}
