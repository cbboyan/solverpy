import os
import logging

from . import markdown
from .markdown import *
from ...tools import human

logger = logging.getLogger(__name__)

def reporter(fun):
   def wrapper(*args, dump=True, prefix="> ", **kwargs):
      rep = fun(*args, **kwargs)
      return markdown.dump(rep, prefix=prefix) if dump else rep
   return wrapper

def typename(obj, quote=""):
   t = type(obj)
   return f"{quote}{t.__module__}.{t.__name__}{quote}"

@reporter
def compress(f_in, size_in, size_z, data, label):
   return [
      newline(),
      heading("Data compression report", level=4),
      text(f"* data file: `{f_in}`"),
      newline(),
      table(["",""], [
         ["uncompressed", human.humanbytes(size_in)],
         ["compressed",   human.humanbytes(size_z)],
         ["ratio",        f"{size_in/size_z:.2f} x"],
         ["data-type",    typename(data, quote="`")],
         ["label-type ",  typename(label, quote="`")]
      ]),
      newline(),
   ]

@reporter
def build(dataname, score, acc, trainacc, f_best, dur, params, pos, neg):
   def valfmt(y):
      return f"{y:g}" if type(y) is float else str(y)
   return [
      newline(),
      heading(f"Model `{dataname}`", level=3),
      heading("Best model statistics", level=4),
      text(f"* best model: `{f_best}`"),
      newline(),
      table(["", ""], [
         [ "trains"      , f"{pos+neg} ({pos} / {neg})" ],
         [ "acc / train" , human.humanacc(trainacc)     ],
         [ "acc / devel" , human.humanacc(acc)          ],
         [ "duration"    , human.humantime(dur)         ],
         [ "score"       , f"{score:0.3f}"              ],
      ]),
      newline(),
      heading("Best model training parameters", level=4),
      table(["param", "value"], [
         [x, valfmt(y)] for (x,y) in params.items()
      ]),
      newline(),
   ]

