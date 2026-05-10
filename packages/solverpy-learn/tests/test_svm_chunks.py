"""
Unit tests for chunked NPZ training data (builder/svm.py).
"""
import io
import os
import numpy as np
import pytest
from sklearn.datasets import load_svmlight_file

from solverpy_learn.builder import svm


def _make_svm_text(n_rows: int, n_features: int = 10, seed: int = 0) -> str:
   rng = np.random.default_rng(seed)
   lines = []
   for _ in range(n_rows):
      label = rng.integers(0, 2)
      features = sorted(rng.choice(n_features, size=3, replace=False) + 1)
      vals = rng.uniform(0.1, 1.0, len(features))
      feat_str = " ".join(f"{f}:{v:.4f}" for f, v in zip(features, vals))
      lines.append(f"{label} {feat_str}\n")
   return "".join(lines)


@pytest.fixture
def svm_file(tmp_path):
   f = str(tmp_path / "train.in")
   with open(f, "w") as fh:
      fh.write(_make_svm_text(250))
   return f


def test_compress_creates_chunks(svm_file):
   svm.compress(svm_file, chunk_size=100)
   assert len(svm.chunkfiles(svm_file)) == 3  # 100 + 100 + 50


def test_compress_removes_text_file(svm_file):
   svm.compress(svm_file, chunk_size=100)
   assert not os.path.isfile(svm_file)


def test_compress_keep_text_file(svm_file):
   svm.compress(svm_file, keep=True, chunk_size=100)
   assert os.path.isfile(svm_file)


def test_compress_skips_if_already_chunked(svm_file):
   svm.compress(svm_file, chunk_size=100)
   n_chunks = len(svm.chunkfiles(svm_file))
   svm.compress(svm_file, chunk_size=100)  # should be a no-op
   assert len(svm.chunkfiles(svm_file)) == n_chunks


def test_ischunked_before_compress(svm_file):
   assert not svm.ischunked(svm_file)


def test_ischunked_after_compress(svm_file):
   svm.compress(svm_file, chunk_size=100)
   assert svm.ischunked(svm_file)


def test_exists_text(svm_file):
   assert svm.exists(svm_file)


def test_exists_chunked(svm_file):
   svm.compress(svm_file, chunk_size=100)
   assert svm.exists(svm_file)


def test_format_text(svm_file):
   assert svm.format(svm_file) == "text/svm"


def test_format_chunked(svm_file):
   svm.compress(svm_file, chunk_size=100)
   assert svm.format(svm_file) == "binary/chunks"


def test_format_unknown(tmp_path):
   assert svm.format(str(tmp_path / "missing")) == "unknown"


def test_load_reproduces_labels(svm_file):
   orig_text = open(svm_file).read()
   (_, orig_label) = load_svmlight_file(io.BytesIO(orig_text.encode()), zero_based=True)
   svm.compress(svm_file, chunk_size=100)
   (_, label) = svm.load(svm_file)
   assert np.array_equal(label, orig_label)


def test_load_reproduces_shape(svm_file):
   orig_text = open(svm_file).read()
   (orig_data, _) = load_svmlight_file(io.BytesIO(orig_text.encode()), zero_based=True)
   svm.compress(svm_file, chunk_size=100)
   (data, _) = svm.load(svm_file)
   assert data.shape == orig_data.shape


def test_size_sums_chunks(svm_file):
   svm.compress(svm_file, chunk_size=100)
   expected = sum(
      os.path.getsize(p) + os.path.getsize(q)
      for (p, q) in svm.chunkfiles(svm_file)
   )
   assert svm.size(svm_file) == expected


def test_link_creates_symlinks(svm_file, tmp_path):
   svm.compress(svm_file, chunk_size=100)
   dst = str(tmp_path / "other" / "train.in")
   svm.link(svm_file, dst)
   dst_chunks = svm.chunkfiles(dst)
   assert len(dst_chunks) == len(svm.chunkfiles(svm_file))
   for (p, q) in dst_chunks:
      assert os.path.islink(p)
      assert os.path.islink(q)


def test_merge_chunk_count(svm_file, tmp_path):
   svm.compress(svm_file, chunk_size=100)  # 3 chunks
   f2 = str(tmp_path / "addon.in")
   with open(f2, "w") as fh:
      fh.write(_make_svm_text(120, seed=1))
   svm.compress(f2, chunk_size=100)  # 2 chunks
   f_out = str(tmp_path / "merged.in")
   svm.merge(svm_file, f2, f_out)
   assert len(svm.chunkfiles(f_out)) == 5


def test_merge_labels_correct(svm_file, tmp_path):
   svm.compress(svm_file, chunk_size=100)
   f2 = str(tmp_path / "addon.in")
   with open(f2, "w") as fh:
      fh.write(_make_svm_text(50, seed=1))
   svm.compress(f2, chunk_size=100)
   f_out = str(tmp_path / "merged.in")
   svm.merge(svm_file, f2, f_out)
   (_, l1) = svm.load(svm_file)
   (_, l2) = svm.load(f2)
   (_, lm) = svm.load(f_out)
   assert np.array_equal(lm, np.concatenate([l1, l2]))


def test_merge_row_count(svm_file, tmp_path):
   svm.compress(svm_file, chunk_size=100)
   f2 = str(tmp_path / "addon.in")
   with open(f2, "w") as fh:
      fh.write(_make_svm_text(50, seed=1))
   svm.compress(f2, chunk_size=100)
   f_out = str(tmp_path / "merged.in")
   svm.merge(svm_file, f2, f_out)
   (d1, _) = svm.load(svm_file)
   (d2, _) = svm.load(f2)
   (dm, _) = svm.load(f_out)
   assert dm.shape[0] == d1.shape[0] + d2.shape[0]
