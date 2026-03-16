"""
# Task management and parallel execution

The `task` module handles parallel execution of solver runs.  A
[`SolverTask`][solverpy.task.solvertask.SolverTask] wraps a single
`(solver, bid, sid, problem)` job.  The
[`Launcher`][solverpy.task.launcher] runs a pool of tasks in parallel
using Python's `multiprocessing`.  Progress is reported through a
[`Talker`][solverpy.task.talker.Talker].

```plantuml name="task-overview"

class solverpy.task.launcher << (M,skyblue) >> {
  + launch(tasks, cores)
  ~ Pool(cores)
}

abstract class solverpy.task.talker.Talker {
  + begin(jobs)
  + next(job)
  + launching(tasks)
  + finished(task, result)
  + done()
  + end(results)
}

class solverpy.task.logtalker.LogTalker extends solverpy.task.talker.Talker
class solverpy.task.solvertalker.SolverTalker extends solverpy.task.logtalker.LogTalker

abstract class solverpy.task.task.Task {
  + run() : Any
  {static} + runtask(task)
}

class solverpy.task.solvertask.SolverTask extends solverpy.task.task.Task

solverpy.task.launcher ..> solverpy.task.solvertask.SolverTask
solverpy.task.solvertalker.SolverTalker ..> solverpy.task.bar.SolvingBar

```

[`LogTalker`][solverpy.task.logtalker.LogTalker] logs progress to the
console/file. [`SolverTalker`][solverpy.task.solvertalker.SolverTalker]
additionally displays a live progress bar using `tqdm`.

"""
