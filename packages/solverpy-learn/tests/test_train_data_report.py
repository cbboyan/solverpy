from types import SimpleNamespace

from solverpy.report.talker.logtalker import LogTalker
from solverpy.report.talker.talker import Talker
from solverpy_learn.builder.plugins.svm import SvmTrains
from solverpy_learn.builder import svm
from solverpy_learn.setups import loop


def test_train_data_snapshot_and_stats(monkeypatch, tmp_path):
   monkeypatch.setenv("SOLVERPY_DB", str(tmp_path))
   trains = SvmTrains("sample")
   path = trains.path()
   raw = svm.raw_path(path, 0)
   raw_text = "1 1:1\n0 2:1\n0 3:1\n"
   tmp_path.joinpath("trains", "sample").mkdir(parents=True)
   tmp_path.joinpath("trains", "sample",
                     "train.in-raw0000").write_text(raw_text)
   assert raw == str(tmp_path / "trains" / "sample" / "train.in-raw0000")
   trains.info.total = 3
   trains.info.pos = 1
   trains.info.neg = 2

   trains.train_data_snapshot()
   stats = trains.train_data_stats("training")

   assert stats is not None
   assert stats["vectors"] == 3
   assert stats["positive"] == 1
   assert stats["negative"] == 2
   assert stats["raw_bytes"] == len(raw_text)
   assert stats["stored_bytes"] == len(raw_text)
   assert stats["format"] == "text/raw-chunks"
   assert stats["chunks"] == 1
   assert stats["files"] == 1


def test_reset_clears_per_file_counts():
   trains = SvmTrains("sample")
   trains.info.total = 7
   trains.info.pos = 2
   trains.info.neg = 5

   trains.reset("next", "addon.in")

   assert trains.info.total == 0
   assert trains.info.pos == 0
   assert trains.info.neg == 0


def test_snapshot_preserves_known_counts_without_new_vectors(
   monkeypatch,
   tmp_path,
):
   monkeypatch.setenv("SOLVERPY_DB", str(tmp_path))
   trains = SvmTrains("sample")
   path = trains.path()
   raw = tmp_path / "trains" / "sample" / "train.in-raw0000"
   raw.parent.mkdir(parents=True)
   raw.write_text("1 1:1\n")
   svm.metadata_save(path, {
      "vectors": 7,
      "positive": 2,
      "negative": 5,
      "raw_bytes": 1,
   })

   trains.train_data_snapshot()

   assert svm.metadata_load(path) == {
      "vectors": 7,
      "positive": 2,
      "negative": 5,
      "raw_bytes": raw.stat().st_size,
   }


def test_log_talker_writes_training_data_table(monkeypatch):
   reports = []
   monkeypatch.setattr(
      "solverpy.report.talker.logtalker.reporter.add",
      reports.append,
   )
   talker = LogTalker()

   talker.train_data([{
      "dataset": "training",
      "path": "trains/run/train.in",
      "format": "binary/chunks",
      "vectors": 30,
      "positive": 10,
      "negative": 20,
      "raw_bytes": 1000,
      "stored_bytes": 250,
      "chunks": 2,
      "files": 4,
   }])

   report = "\n".join(reports[0])
   assert "### Training data" in report
   assert "| key" in report and "| val" in report
   assert "#### training `trains/run/train.in`" in report
   assert "trains/run/train.in" in report
   assert "vectors" in report
   assert "30" in report
   assert "neg/pos" in report
   assert "2.00:1" in report
   assert "ratio" in report
   assert "4.00x" in report


def test_oneloop_reports_generated_and_merged_files(monkeypatch):

   class FakeTrains:

      def __init__(self):
         self.filename = "addon.in"
         self.snapshots = 0

      def path(self, dataname=None, filename=None):
         del dataname
         return filename or self.filename

      def train_data_snapshot(self):
         self.snapshots += 1

      def train_data_stats(self, dataset, path=None):
         path = path or self.path()
         return {
            "dataset": dataset,
            "path": path,
            "format": "binary/chunks",
            "stored_bytes": 10,
            "chunks": 1,
            "files": 2,
         }

      def exists(self):
         return True

      def merge(self, previous, filename):
         assert previous == "previous.in"
         assert filename == "train.in"

      def reset(self, dataname=None, filename="train.in"):
         del dataname
         self.filename = filename

   class RecordingTalker(Talker):

      def __init__(self):
         super().__init__()
         self.stats = []

      def train_data(self, stats):
         self.stats.append(stats)

   trains = FakeTrains()
   talker = RecordingTalker()
   evalset = {
      "dataname": "sample/loop01",
      "label": "development",
      "previous_trains": "previous.in",
      "plugin": trains,
   }
   setup = {
      "it": 1,
      "loops": 2,
      "options": [],
   }
   monkeypatch.setattr(loop.evaluator, "launch", lambda *args, **kwargs: None)
   monkeypatch.setattr(loop.reporter, "add", lambda report: None)
   monkeypatch.setattr(loop, "resource_summary", lambda *args: "")
   monkeypatch.setattr(loop, "usage", lambda *args: "")

   setup["talker"] = talker
   loop.oneloop(setup, evalset)

   assert trains.snapshots == 1
   assert [[stat["path"] for stat in stats]
           for stats in talker.stats] == [["addon.in", "train.in"]]
   assert all(stat["dataset"] == "development" for stat in talker.stats[0])


def test_iteration_applies_both_start_datanames_before_build(monkeypatch):

   class FakeTrains:

      def __init__(self, dataname):
         self.dataname = dataname

      def reset(self, dataname=None, filename="train.in"):
         del filename
         if dataname is not None:
            self.dataname = dataname

      def path(self):
         return self.dataname

      def train_data_stats(self, dataset, paths=None):
         del paths
         return {"dataset": dataset, "path": self.path()}

   class FakeBuilder:

      strategies = ["new"]

      def build(self, talker):
         del talker
         self.paths = (
            setup["trains"]["plugin"].path(),
            setup["devels"]["plugin"].path(),
         )

   talker = SimpleNamespace(train_data=lambda stats: None)
   builder = FakeBuilder()
   setup = {
      "it": 0,
      "loops": 1,
      "options": [],
      "talker": talker,
      "builder": builder,
      "trains": {
         "dataname": "train/loop00",
         "label": "training",
         "start_dataname": "old/train/loop00",
         "plugin": FakeTrains("train/loop00"),
      },
      "devels": {
         "dataname": "devel/loop00",
         "label": "development",
         "start_dataname": "old/devel/loop00",
         "plugin": FakeTrains("devel/loop00"),
      },
   }
   monkeypatch.setattr(loop.evaluator, "launch", lambda *args, **kwargs: None)
   monkeypatch.setattr(loop.reporter, "add", lambda report: None)
   monkeypatch.setattr(loop, "resource_summary", lambda *args: "")
   monkeypatch.setattr(loop, "usage", lambda *args: "")

   loop.iteration(setup)

   assert builder.paths == ("old/train/loop00", "old/devel/loop00")
