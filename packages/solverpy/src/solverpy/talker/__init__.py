"""
# Talker — progress reporters for benchmark evaluation

Contains the talker class hierarchy for reporting evaluation and tuning
progress.

```plantuml name="talker-overview"

abstract class solverpy.talker.talker.Talker {
  + begin(jobs)
  + next(job)
  + launching(tasks)
  + finished(task, result)
  + done()
  + end(results)
}

class solverpy.talker.logtalker.LogTalker extends solverpy.talker.talker.Talker
class solverpy.talker.solvertalker.SolverTalker extends solverpy.talker.logtalker.LogTalker
class solverpy.talker.remotetalker.RemoteTalker extends solverpy.talker.talker.Talker

solverpy.talker.solvertalker.SolverTalker ..> solverpy.talker.bar.SolvingBar

```

[`LogTalker`][solverpy.talker.logtalker.LogTalker] logs progress to the
console/file. [`SolverTalker`][solverpy.talker.solvertalker.SolverTalker]
additionally displays a live progress bar using `tqdm`.
[`RemoteTalker`][solverpy.talker.remotetalker.RemoteTalker] is a cross-process
proxy that forwards method calls from a child process to the parent.
"""
