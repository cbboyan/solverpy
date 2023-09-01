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

def save(data, label, f_in):
   (z_data, z_label) = datafiles(f_in)
   logger.debug(f"saving compressed data to {f_in}")
   logger.debug(f"> | shape        | {data.shape[0]}x{data.shape[1]} |")
   logger.debug(f"> | values       | {data.nnz} | ")
   logger.debug(f"> | format       | {data.format} |")
   scipy.sparse.save_npz(z_data, data, compressed=True)
   logger.debug(f"saving compressed labels to {z_label}")
   numpy.savez_compressed(z_label, label=label)
   logger.debug(f"> | compressed   | {human.humanbytes(size(f_in))} |")

def compress(f_in, keep=False):
   logger.info(f"Compressing trains of size {human.humanbytes(size(f_in))} from `{f_in}`.")
   if iscompressed(f_in):
      logger.warning(f"Trains {f_in} are already compressed.  Skipped.")
      return
   logger.debug(f"> | uncompressed | {human.humanbytes(size(f_in))} |")
   (data, label) = load_svmlight_file(f_in, zero_based=True)
   save(data, label, f_in)
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

def merge(f_in1=None, f_in2=None, data1=None, data2=None, f_out=None):
   if f_in1 and f_in2:
      logger.info(f"Merging trains: {f_in1} and {f_in2}")
   (d1,l1) = data1 if data1 else load(f_in1)
   (d2,l2) = data2 if data2 else load(f_in2)
   logger.info(f"Merging data of shapes: {d1.shape[0]}x{d1.shape[1]} and {d2.shape[0]}x{d2.shape[1]}")
   d = scipy.sparse.vstack((d1, d2))
   logger.info(f"Merging labels of shapes: {l1.shape[0]} and {l2.shape[0]}")
   l = numpy.concatenate((l1, l2))
   if f_out:
      save(d, l, f_out)
   return (d,l)

