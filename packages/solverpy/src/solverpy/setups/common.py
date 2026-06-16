from typing import Any, TYPE_CHECKING
import logging

from ..solver import plugins
from .setup import Setup

if TYPE_CHECKING:
   from ..tools.typing import SolverMaker

logger = logging.getLogger(__name__)

# generic arguments accepted by solver constructors
GENERICS = frozenset(["binary", "plugins", "static", "complete"])


def default(setup: Any, key: str, val: Any) -> None:
   if key not in setup:
      setup[key] = val


def ensure(options: list[str], option: str) -> None:
   baseopt = option if not option.startswith("no-") else option[3:]
   if (baseopt not in options) and (f"no-{baseopt}" not in options):
      options.append(option)


def init(setup: Setup) -> Setup:
   default(setup, "options", ["flatten", "compress"])
   assert "options" in setup
   options = setup["options"]
   ensure(options, "flatten")
   ensure(options, "compress")
   default(setup, "limit", "T1")
   default(setup, "dataname", "noname")

   if "plugins" not in setup:
      if "outputs" not in options:
         plugs = plugins.db()
      else:
         plugs = plugins.outputs(
            flatten="flatten" in options,
            compress="compress" in options,
         )
      if "proofs" in options or "premises" in options:
         plugs.append(plugins.Proofs(
            proof="proofs" in options,
            premises="premises" in options,
            flatten="flatten" in options,
            compress="compress" in options,
         ))
      default(setup, "plugins", plugs)
   return setup


def make_solver(
   setup: Setup,
   mk_solver: "SolverMaker",
   plugins: list | None = None,
   reloader: bool = False,
   options: list[str] | None = None,
):
   assert "static" in setup
   assert "limit" in setup
   kwargs = {x: setup[x] for x in setup if x in GENERICS}
   if plugins is not None:
      kwargs["plugins"] = plugins
   kwargs["static"] = " ".join(setup["static"])
   _solver = mk_solver(setup["limit"], **kwargs)
   if reloader:
      from ..solver.reloader import Reloader
      options = options or []
      _solver = Reloader(
         _solver,
         flatten="flatten" in options,
         compress="compress" in options,
      )
   return _solver
