"""
# Talker — progress reporters for benchmark evaluation

Contains the talker class hierarchy for reporting evaluation and tuning
progress.

```plantuml name="talker-overview"

abstract class solverpy.report.talker.talker.Talker {
  + begin(jobs)
  + next(job)
  + launching(tasks)
  + finished(task, result)
  + done()
  + end(results)
}

class solverpy.report.talker.logtalker.LogTalker extends solverpy.report.talker.talker.Talker
class solverpy.report.talker.solvertalker.SolverTalker extends solverpy.report.talker.logtalker.LogTalker
class solverpy.report.talker.remotetalker.RemoteTalker extends solverpy.report.talker.talker.Talker

solverpy.report.talker.solvertalker.SolverTalker ..> solverpy.report.talker.bar.SolvingBar

```

[`LogTalker`][solverpy.report.talker.logtalker.LogTalker] logs progress to the
console/file. [`SolverTalker`][solverpy.report.talker.solvertalker.SolverTalker]
additionally displays a live progress bar using `tqdm`.
[`RemoteTalker`][solverpy.report.talker.remotetalker.RemoteTalker] is a cross-process
proxy that forwards method calls from a child process to the parent.
"""
