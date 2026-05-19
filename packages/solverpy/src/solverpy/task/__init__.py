"""
# Task management and parallel execution

The `task` module handles parallel execution of solver runs.  A
[`SolverTask`][solverpy.task.solvertask.SolverTask] wraps a single
`(solver, bid, sid, problem)` job.  The
[`Launcher`][solverpy.task.launcher] runs a pool of tasks in parallel
using Python's `multiprocessing`.  Progress is reported through a
[`Talker`][solverpy.talker.talker.Talker] from the
[`solverpy.talker`][solverpy.talker] package.

```plantuml name="task-overview"

class solverpy.task.launcher << (M,skyblue) >> {
  + launch(tasks, cores)
  ~ Pool(cores)
}

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

abstract class solverpy.task.task.Task {
  + run() : Any
  {static} + runtask(task)
}

class solverpy.task.solvertask.SolverTask extends solverpy.task.task.Task

solverpy.task.launcher ..> solverpy.task.solvertask.SolverTask
solverpy.talker.solvertalker.SolverTalker ..> solverpy.talker.bar.SolvingBar

```

"""
