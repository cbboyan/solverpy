from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
   from ..benchmark.db.provider import Provider

ProviderMaker = Callable[[str, str, str], "Provider"]

StrMaker = str | Callable[[Any], str]

Builder = dict[str, StrMaker]

Result = dict[str, Any]

