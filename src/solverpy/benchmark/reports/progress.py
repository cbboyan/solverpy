from typing import Callable, TYPE_CHECKING
import logging

from . import markdown
from .markdown import *
from ...tools import human

if TYPE_CHECKING:
   from ...tools.typing import Report

logger = logging.getLogger(__name__)

#def reporter(fun: Callable[..., "Report"]) -> Callable[..., "Report"]:
#   def wrapper(*args, dump=True, prefix="> ", **kwargs) -> "Report":
#      rep = fun(*args, **kwargs)
#      return markdown.dump(rep, prefix=prefix) if dump else rep

def reporter(fun: Callable[..., "Report"]) -> Callable[..., str]:
   def wrapper(*args, prefix="> ", **kwargs) -> str:
      rep = fun(*args, **kwargs)
      return markdown.dump(rep, prefix=prefix) 

   return wrapper


def typename(obj: object, quote: str = ""):
   t = type(obj)
   return f"{quote}{t.__module__}.{t.__name__}{quote}"


@reporter
def compress(
   f_in: str,
   size_in: int,
   size_z: int,
   data: object,
   label: object,
) -> "Report":
   return [
      newline(),
      heading("Data compression report", level=4),
      text(f"* data file: `{f_in}`"),
      newline(),
      table(["", ""],
            [["uncompressed", human.humanbytes(size_in)],
             ["compressed", human.humanbytes(size_z)],
             ["ratio", f"{size_in/size_z:.2f} x"],
             ["data-type", typename(data, quote="`")],
             ["label-type ", typename(label, quote="`")]]),
      newline(),
   ]


@reporter
def build(
   dataname: str,
   score: float,
   acc: float,
   trainacc: float,
   f_best: str,
   dur: float,
   params: dict[str, int | float | str],
   pos: int,
   neg: int,
) -> "Report":

   def valfmt(y: int | float | str) -> str:
      return f"{y:g}" if type(y) is float else str(y)

   return [
      newline(),
      heading(f"Model `{dataname}`", level=3),
      heading("Best model statistics", level=4),
      text(f"* best model: `{f_best}`"),
      newline(),
      table(["", ""], [
         ["trains", f"{pos+neg} ({pos} / {neg})"],
         ["acc / train", human.humanacc(trainacc)],
         ["acc / devel", human.humanacc(acc)],
         ["duration", human.humantime(dur)],
         ["score", f"{score:0.3f}"],
      ]),
      newline(),
      heading("Best model training parameters", level=4),
      table(["param", "value"], [[x, valfmt(y)] for (x, y) in params.items()]),
      newline(),
   ]
