import pytest
from pathlib import Path

_GRACKLE_TESTS = str(Path(__file__).parent)


def pytest_collection_modifyitems(items):
   for item in items:
      if str(item.fspath).startswith(_GRACKLE_TESTS):
         item.add_marker(pytest.mark.grackle)
