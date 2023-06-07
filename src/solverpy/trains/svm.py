import os
import logging

import numpy
import scipy
from sklearn.datasets import load_svmlight_file, dump_svmlight_file

from ..tools import human

logger = logging.getLogger(__name__)

def datafiles(f_in):
   z_data = f_in + "-data.npz"
   z_label = f_in + "-label.npz"
   return [z_data, z_label]

def iscompressed(f_in):
   return all(map(os.path.isfile, datafiles(f_in)))

def exists(f_in):
   return iscompressed(f_in) or os.path.isfile(f_in)

def size(f_in):
   if iscompressed(f_in):
      return sum(os.path.getsize(f) for f in datafiles(f_in))
   else:
      return os.path.getsize(f_in)

def format(f_in):
   if iscompressed(f_in):
      return "binary/npz"
   if os.path.isfile(f_in):
      return "text/svm"
   return "unknown"

def compress(f_in, keep=False):
   logger.info(f"Compressing trains of size {human.humanbytes(size(f_in))} from `{f_in}`.")
   if iscompressed(f_in):
      logger.warning(f"Trains {f_in} are already compressed.  Skipped.")
      return
   logger.debug("uncompressed size: %s" % human.humanbytes(size(f_in)))
   (data, label) = load_svmlight_file(f_in, zero_based=True)
   (z_data, z_label) = datafiles(f_in)
   logger.debug(f"compressing data to {z_data}")
   scipy.sparse.save_npz(z_data, data, compressed=True)
   logger.debug(f"compressing labels to {z_label}")
   numpy.savez_compressed(z_label, label=label)
   logger.debug(f"compressed size: {human.humanbytes(size(f_in))}")
   if iscompressed(f_in) and not keep:
      logger.debug(f"deleting the uncompressed file")
      os.remove(f_in)
   logger.info(f"Trains compressed to {human.humanbytes(size(f_in))}.")

def decompress(f_in, keep=True):
   logger.info(f"Decompressing trains of size {human.humanbytes(size(f_in))} from `{f_in}`.")
   if not iscompressed(f_in):
      logger.warning(f"Trains `{f_in}` are not compressed.  Skipped.")
      return
   (data, label) = load(f_in)
   logger.debug(f"dumping trains to {f_in}")
   dump_svmlight_file(data, label, f_in)
   logger.debug(f"trains dumped; uncompressed size: {human.humanbytes(os.path.getsize(f_in))}")
   if os.path.isfile(f_in) and not keep:
      logger.debug(f"deleting the compressed files")
      for f in datafiles(f_in):
         os.remove(f)
   logger.info(f"Trains decompressed to {human.humanbytes(os.path.getsize(f_in))}.")

def load(f_in):
   logger.info(f"Loading trains of size {human.humanbytes(size(f_in))} from `{f_in}`.")
   if iscompressed(f_in): 
      logger.debug(f"loading compressed data")
      (z_data, z_label) = datafiles(f_in)
      data = scipy.sparse.load_npz(z_data)
      label = numpy.load(z_label, allow_pickle=True)["label"]
      logger.debug(f"compressed data loaded")
   else:
      logger.debug(f"loading uncompressed data")
      (data, label) = load_svmlight_file(f_in, zero_based=True)
      logger.debug(f"uncompressed data loaded")
   logger.info("Trains loaded.")
   return (data, label)

