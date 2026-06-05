"""
# Task management and parallel execution

The `task` module handles parallel execution of solver runs.  A
[`SolverTask`][solverpy.task.solvertask.SolverTask] wraps a single
`(solver, bid, sid, problem)` job.  The
[`Launcher`][solverpy.task.launcher] runs a pool of tasks in parallel
using Python's `multiprocessing`.  Progress is reported through a
[`Talker`][solverpy.report.talker.talker.Talker] from the
[`solverpy.report.talker`][solverpy.report.talker] package.

```plantuml name="task-overview"

class solverpy.task.launcher << (M,skyblue) >> {
  + launch(tasks, cores)
  ~ Pool(cores)
}

abstract class solverpy.report.talker.talker.Talker {
  + begin(jobs)
  + next(job)
  + launching(tasks)
  + finished(task, result)
  + done()
  + end(results)
}

class solverpy.report.talker.logtalker.LogTalker extends solverpy.report.talker.talker.Talker
class solverpy.report.talker.evaltalker.EvalTalker extends solverpy.report.talker.logtalker.LogTalker

abstract class solverpy.task.task.Task {
  + run() : Any
  {static} + runtask(task)
}

class solverpy.task.solvertask.SolverTask extends solverpy.task.task.Task

solverpy.task.launcher ..> solverpy.task.solvertask.SolverTask
solverpy.report.talker.evaltalker.EvalTalker ..> solverpy.report.talker.bar.SolvingBar

```

"""
